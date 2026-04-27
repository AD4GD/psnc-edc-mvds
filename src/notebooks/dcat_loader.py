"""
DCAT Loader - usage guide

Author: Mateusz Świercz
Creation date: 2026-04-27

Required libraries:
- requests
- python-keycloak

Installation (example):
    pip install requests python-keycloak

Run from CLI:
1) Fill in the .env file (by default next to this script) with required values,
   including CATALOG_URL, MANAGEMENT_API, and authentication settings.
2) Run:
    python dcat_loader.py

Optionally, you can use a different env file:
    ENV_FILE=/path/to/.env python dcat_loader.py
"""

import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError

import requests

from dataspace_apis import create_asset, create_contract_definition, create_policy, update_asset


LOGGER = logging.getLogger("dcat_loader")

DEFAULT_CONTEXT = {
    "edc": "https://w3id.org/edc/v0.0.1/ns/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "geo": "http://www.opengis.net/ont/geosparql#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "owl": "http://www.w3.org/2002/07/owl#",
}

METADATA_BLACKLIST = {
    "@id",
    "@type",
    "dct:identifier",
    "dct:title",
}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        LOGGER.warning("Env file not found at %s; using process environment only.", env_path)
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            LOGGER.warning("Ignoring malformed env line: %s", raw_line)
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def as_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def get_required_env(name: str) -> str:
    value = env(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def with_timeout() -> int:
    raw = env("REQUEST_TIMEOUT_SECONDS", "20")
    try:
        timeout = int(raw)
    except (TypeError, ValueError):
        LOGGER.warning("Invalid REQUEST_TIMEOUT_SECONDS=%s. Falling back to 20.", raw)
        return 20
    return max(timeout, 1)


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def fetch_json(url: str, timeout_seconds: int) -> Any:
    if not is_http_url(url):
        raise ValueError(f"CATALOG_URL is not a valid HTTP URL: {url}")

    response = requests.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as exc:
        raise ValueError(f"Response from {url} is not valid JSON") from exc


def looks_like_dcat(payload: Any) -> Tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "Top-level JSON must be an object."

    if "dcat:dataset" not in payload:
        return False, "Missing dcat:dataset in top-level object."

    datasets = payload.get("dcat:dataset")
    if not isinstance(datasets, list) or len(datasets) == 0:
        return False, "dcat:dataset must be a non-empty list."

    context = payload.get("@context")
    has_dcat_context = False
    if isinstance(context, dict):
        for key, val in context.items():
            key_txt = str(key).lower()
            val_txt = str(val).lower()
            if key_txt == "dcat" or "dcat" in val_txt:
                has_dcat_context = True
                break

    has_dataset_hint = any(isinstance(item, dict) and "dcat:distribution" in item for item in datasets)

    if not has_dcat_context and not has_dataset_hint:
        return False, "Payload does not contain DCAT context or dataset distribution fields."

    return True, "ok"


def make_headers(api_key: Optional[str] = None, bearer_token: Optional[str] = None) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    return headers


def test_management_access(management_api: str, headers: Dict[str, str], timeout_seconds: int) -> bool:
    endpoint = f"{management_api.rstrip('/')}/v3/assets/request"
    payload = {
        "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
        "@type": "QuerySpec",
        "limit": 1,
        "offset": 0,
    }
    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=timeout_seconds)
        if response.status_code in {200, 204}:
            return True
        LOGGER.warning("Management API auth test failed: %s %s", response.status_code, response.text[:300])
        return False
    except requests.RequestException as exc:
        LOGGER.warning("Management API auth test error: %s", exc)
        return False


def parse_keycloak_server_and_realm(keycloak_url: str, fallback_realm: str) -> Tuple[str, str]:
    parsed = urlparse(keycloak_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid KEYCLOAK_URL: {keycloak_url}")

    path = parsed.path.rstrip("/")
    protocol_suffix = "/protocol/openid-connect"
    if protocol_suffix in path:
        path = path.split(protocol_suffix, 1)[0]

    realm_match = re.search(r"/realms/([^/]+)$", path)
    realm_name = fallback_realm
    base_path = path
    if realm_match:
        realm_name = realm_match.group(1)
        base_path = path[: realm_match.start()]

    server_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"
    if not server_url.endswith("/"):
        server_url += "/"

    return server_url, realm_name


def obtain_token_from_keycloak(timeout_seconds: int) -> Optional[str]:
    kc_url = env("KEYCLOAK_URL")
    username = env("USERNAME")
    password = env("PASSWORD")

    if not kc_url or not username or not password:
        LOGGER.warning("Credential auth unavailable: KEYCLOAK_URL/USERNAME/PASSWORD not fully configured.")
        return None

    client_id = env("KEYCLOAK_CLIENT_ID", "admin-cli")
    client_secret = env("KEYCLOAK_CLIENT_SECRET")
    grant_type = env("KEYCLOAK_GRANT_TYPE", "password")
    realm_name = env("KEYCLOAK_REALM", "master")
    verify_tls = as_bool(env("KEYCLOAK_VERIFY_TLS", "true"), default=True)

    try:
        server_url, resolved_realm = parse_keycloak_server_and_realm(kc_url, realm_name)
    except ValueError as exc:
        LOGGER.warning("%s", exc)
        return None

    try:
        keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            realm_name=resolved_realm,
            client_id=client_id,
            client_secret_key=client_secret,
            verify=verify_tls,
            timeout=timeout_seconds,
        )
        token_payload = keycloak_openid.token(
            username=username,
            password=password,
            grant_type=grant_type,
        )
        access_token = token_payload.get("access_token")
        if not access_token:
            LOGGER.warning("Token response has no access_token.")
            return None
        return str(access_token)
    except KeycloakError as exc:
        LOGGER.warning("Token request failed via python-keycloak: %s", exc)
        return None
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Token request error via python-keycloak: %s", exc)
        return None


def authenticate(management_api: str, timeout_seconds: int) -> Dict[str, str]:
    login_mode = env("LOGIN_MODE", "api_key")
    api_key = env("API_KEY")

    # Always try api_key first when available, per requirement.
    if api_key:
        headers = make_headers(api_key=api_key)
        if test_management_access(management_api, headers, timeout_seconds):
            LOGGER.info("Authenticated with API key.")
            return headers
        LOGGER.warning("API key auth failed; trying username/password Keycloak flow.")
    elif login_mode == "api_key":
        LOGGER.warning("LOGIN_MODE=api_key but API_KEY is empty; falling back to credential auth.")

    token = obtain_token_from_keycloak(timeout_seconds)
    if token:
        headers = make_headers(bearer_token=token)
        if test_management_access(management_api, headers, timeout_seconds):
            LOGGER.info("Authenticated with Keycloak bearer token.")
            return headers
        LOGGER.warning("Credential auth produced token but management access still failed.")

    raise RuntimeError("Authentication failed (API key and credential methods unavailable or invalid).")


def normalize_to_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def get_access_url(distribution: Dict[str, Any]) -> Optional[str]:
    access = distribution.get("dcat:accessURL")
    if isinstance(access, dict):
        if "@id" in access and isinstance(access["@id"], str):
            return access["@id"].strip() or None
    if isinstance(access, str):
        return access.strip() or None
    return None


def sanitize_identifier(raw: str, fallback: str) -> str:
    candidate = raw.strip() if raw else fallback
    cleaned = re.sub(r"[^a-zA-Z0-9._:-]", "_", candidate)
    cleaned = cleaned[:240].strip("_")
    return cleaned or fallback


def normalize_content_type(raw_format: Any) -> str:
    default_content_type = "application/json"
    if raw_format is None:
        return default_content_type

    if isinstance(raw_format, dict):
        raw_format = raw_format.get("@id")

    if not isinstance(raw_format, str):
        return default_content_type

    value = raw_format.strip().lower()
    if not value:
        return default_content_type

    # Accept valid mime-like values directly.
    if re.match(r"^[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+$", value):
        return value

    # Heuristics for common DCAT formats and URL-like values.
    if "json" in value:
        return "application/json"
    if "csv" in value:
        return "text/csv"
    if "xml" in value:
        return "application/xml"

    LOGGER.warning("Unsupported dct:format value '%s'. Falling back to application/json.", raw_format)
    return default_content_type


def is_supported_dcat_metadata_key(key: str) -> bool:
    return bool(re.match(r"^(dct|dcat):[A-Za-z0-9._-]+$", key))


def normalize_whitespace_in_string(value: str) -> str:
    # Flatten tabs/newlines and trim repeated spaces to keep metadata readable.
    value = value.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").replace("\t", " ")
    value = re.sub(r"\s{2,}", " ", value)
    return value.strip()


def normalize_whitespace_in_value(value: Any) -> Any:
    if isinstance(value, str):
        return normalize_whitespace_in_string(value)
    if isinstance(value, list):
        return [normalize_whitespace_in_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_whitespace_in_value(val) for key, val in value.items()}
    return value


def build_metadata(dataset: Dict[str, Any], distribution: Dict[str, Any], access_url: str) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}

    for raw_key, value in dataset.items():
        if value is None or not isinstance(raw_key, str):
            continue
        if raw_key in METADATA_BLACKLIST:
            continue
        if not is_supported_dcat_metadata_key(raw_key):
            continue
        if raw_key == "dcat:distribution":
            continue
        metadata[raw_key] = normalize_whitespace_in_value(value)

    # Keep only the currently processed distribution in metadata.
    metadata["dcat:distribution"] = normalize_whitespace_in_value(normalize_to_list(distribution))

    return metadata


def build_asset_payload(dataset: Dict[str, Any], distribution: Dict[str, Any], index: int) -> Tuple[str, str, str, str, Dict[str, Any]]:
    dataset_identifier = str(dataset.get("dct:identifier") or dataset.get("@id") or f"dataset-{index}")
    title = str(dataset.get("dct:title") or dataset_identifier)

    access_url = get_access_url(distribution)
    if not access_url:
        raise ValueError("Distribution has no valid dcat:accessURL.")

    fmt = distribution.get("dct:format")
    content_type = normalize_content_type(fmt)

    distribution_identifier = distribution.get("dct:identifier")
    suffix = str(distribution_identifier or access_url)
    asset_id = sanitize_identifier(f"{dataset_identifier}-{suffix}", f"dataset-{index}")

    metadata = build_metadata(dataset, distribution, access_url)

    return asset_id, title, access_url, content_type, metadata


def ensure_policy_exists(management_api: str, headers: Dict[str, str], policy_id: str) -> None:
    response = create_policy(policy_id=policy_id, management_url=management_api, default_headers=headers, permissions=[])
    if response.status_code in {200, 201, 204, 409}:
        if response.status_code == 409:
            LOGGER.info("Policy %s already exists.", policy_id)
        else:
            LOGGER.info("Policy %s ensured (status=%s).", policy_id, response.status_code)
        return
    raise RuntimeError(f"Failed to create/ensure policy {policy_id}: {response.status_code} {response.text[:300]}")


def create_offer_for_distribution(
    management_api: str,
    headers: Dict[str, str],
    policy_id: str,
    dataset: Dict[str, Any],
    distribution: Dict[str, Any],
    index: int,
    proxy_enabled: bool,
) -> Dict[str, Any]:
    asset_id, title, access_url, content_type, metadata = build_asset_payload(dataset, distribution, index)
    contract_definition_id = sanitize_identifier(f"cd_{asset_id}", f"cd_dataset_{index}")

    create_response = create_asset(
        asset_id=asset_id,
        management_url=management_api,
        default_headers=headers,
        asset_name=title,
        content_type=content_type,
        baseUrl=access_url,
        additional_metadata=metadata,
        context=DEFAULT_CONTEXT,
        proxy=proxy_enabled,
    )

    if create_response.status_code == 409:
        LOGGER.info("Asset %s already exists, trying update.", asset_id)
        update_response = update_asset(
            asset_id=asset_id,
            management_url=management_api,
            default_headers=headers,
            asset_name=title,
            content_type=content_type,
            baseUrl=access_url,
            additional_metadata=metadata,
            context=DEFAULT_CONTEXT,
            proxy=proxy_enabled,
        )
        if update_response.status_code not in {200, 201, 204}:
            raise RuntimeError(
                f"Failed to update asset {asset_id}: {update_response.status_code} {update_response.text[:300]}"
            )
    elif create_response.status_code not in {200, 201, 204}:
        raise RuntimeError(f"Failed to create asset {asset_id}: {create_response.status_code} {create_response.text[:300]}")

    contract_response = create_contract_definition(
        contract_definition_id=contract_definition_id,
        management_url=management_api,
        asset_id=asset_id,
        policy_id=policy_id,
        default_headers=headers,
    )

    if contract_response.status_code not in {200, 201, 204, 409}:
        raise RuntimeError(
            f"Failed to create contract definition {contract_definition_id}: "
            f"{contract_response.status_code} {contract_response.text[:300]}"
        )

    return {
        "asset_id": asset_id,
        "contract_definition_id": contract_definition_id,
        "asset_status": create_response.status_code,
        "contract_status": contract_response.status_code,
    }


def process_catalog(payload: Dict[str, Any], management_api: str, headers: Dict[str, str]) -> None:
    policy_id = env("POLICY_ID", "test-policy")
    proxy_enabled = as_bool(env("PROXY_ENABLED", "true"), default=True)
    sleep_seconds_raw = env("SLEEP_SECONDS", "0.02")
    try:
        sleep_seconds = max(0.0, float(sleep_seconds_raw))
    except (TypeError, ValueError):
        LOGGER.warning("Invalid SLEEP_SECONDS=%s. Falling back to 0.02.", sleep_seconds_raw)
        sleep_seconds = 0.02

    ensure_policy_exists(management_api, headers, policy_id)

    datasets = payload.get("dcat:dataset", [])
    created = 0
    skipped = 0
    failed = 0

    for dataset_idx, dataset in enumerate(datasets, start=1):
        if not isinstance(dataset, dict):
            skipped += 1
            LOGGER.warning("Skipping dataset #%s: dataset is not an object.", dataset_idx)
            continue

        distributions = normalize_to_list(dataset.get("dcat:distribution"))
        if not distributions:
            skipped += 1
            LOGGER.warning("Skipping dataset #%s: no dcat:distribution field.", dataset_idx)
            continue

        for dist_idx, distribution in enumerate(distributions, start=1):
            if not isinstance(distribution, dict):
                skipped += 1
                LOGGER.warning("Skipping dataset #%s distribution #%s: not an object.", dataset_idx, dist_idx)
                continue

            try:
                result = create_offer_for_distribution(
                    management_api=management_api,
                    headers=headers,
                    policy_id=policy_id,
                    dataset=dataset,
                    distribution=distribution,
                    index=(dataset_idx * 1000 + dist_idx),
                    proxy_enabled=proxy_enabled,
                )
                created += 1
                LOGGER.info(
                    "Created offer: asset=%s contract=%s",
                    result["asset_id"],
                    result["contract_definition_id"],
                )
            except Exception as exc:  # noqa: BLE001
                failed += 1
                LOGGER.error(
                    "Failed processing dataset #%s distribution #%s: %s",
                    dataset_idx,
                    dist_idx,
                    exc,
                )

            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

    LOGGER.info("Finished. created=%s skipped=%s failed=%s", created, skipped, failed)


def main() -> int:
    configure_logging()

    script_dir = Path(__file__).resolve().parent
    env_path = Path(env("ENV_FILE", str(script_dir / ".env")))
    load_env_file(env_path)

    try:
        catalog_url = get_required_env("CATALOG_URL")
        management_api = get_required_env("MANAGEMENT_API")
        timeout_seconds = with_timeout()

        payload = fetch_json(catalog_url, timeout_seconds)
        valid, reason = looks_like_dcat(payload)
        if not valid:
            LOGGER.warning("Input JSON is not DCAT compatible: %s", reason)
            return 1

        headers = authenticate(management_api, timeout_seconds)
        process_catalog(payload, management_api, headers)
        return 0
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Fatal error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
