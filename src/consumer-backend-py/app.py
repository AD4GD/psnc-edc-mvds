import datetime
import io
import logging
import mimetypes
import os
import posixpath
import re
from typing import List, Optional
from urllib.parse import parse_qsl, urlencode, urlparse

import boto3
import filetype
import httpx
import uvicorn
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

IP = "0.0.0.0"  # nosec
PORT = 4000  # nosec

INTERNAL_QUERY_PARAM_KEYS = {
    "requester",
    "requesterparticipant",
    "requestedby",
    "participant",
    "folder",
}


class DataAddressProperties(BaseModel):
    type: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/type")
    endpoint: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/endpoint")
    auth_type: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/authType")
    endpoint_type: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/endpointType")
    authorization: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/authorization")


class DataAddress(BaseModel):
    properties: DataAddressProperties


class CallbackAddress(BaseModel):
    uri: str
    events: List[str]
    transactional: bool
    auth_key: Optional[str] = Field(None, alias="authKey")
    auth_code_id: Optional[str] = Field(None, alias="authCodeId")


class Payload(BaseModel):
    transfer_process_id: str = Field(..., alias="transferProcessId")
    callback_addresses: List[CallbackAddress] = Field(..., alias="callbackAddresses")
    asset_id: str = Field(..., alias="assetId")
    type: str
    contract_id: str = Field(..., alias="contractId")
    data_address: DataAddress = Field(..., alias="dataAddress")


class TransferProcessStarted(BaseModel):
    id: str
    at: int
    payload: Payload
    type: str


def get_storage_credentials():
    return {
        "endpoint": os.environ.get("STORAGE_ENDPOINT"),
        "access_key": os.environ.get("STORAGE_ACCESS_KEY"),
        "secret_key": os.environ.get("STORAGE_SECRET_KEY"),
        "is_secure": os.environ.get("STORAGE_IS_SECURE"),
    }


def _env_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def get_s3_config():
    endpoint_url = os.environ.get("S3_ENDPOINT_URL")

    # Backward-compatible: accept STORAGE_ENDPOINT with or without scheme.
    if not endpoint_url:
        storage_data = get_storage_credentials()
        endpoint = (storage_data.get("endpoint") or "").strip() if storage_data else ""
        is_secure = _env_bool(storage_data.get("is_secure"), default=False)
        if endpoint:
            if endpoint.startswith("http://") or endpoint.startswith("https://"):
                endpoint_url = endpoint
            else:
                scheme = "https" if is_secure else "http"
                endpoint_url = f"{scheme}://{endpoint}"

    access_key = os.environ.get("S3_ACCESS_KEY") or os.environ.get("STORAGE_ACCESS_KEY")
    secret_key = os.environ.get("S3_SECRET_KEY") or os.environ.get("STORAGE_SECRET_KEY")

    bucket = os.environ.get("S3_BUCKET") or os.environ.get("STORAGE_BUCKET") or "downloads"
    region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("S3_REGION") or "us-east-1"
    prefix = os.environ.get("S3_DEFAULT_PREFIX") or os.environ.get("S3_PREFIX") or "default"
    default_folder = os.environ.get("S3_DEFAULT_FOLDER") or os.environ.get("STORAGE_DEFAULT_FOLDER") or "default"

    return {
        "endpoint_url": endpoint_url,
        "access_key": access_key,
        "secret_key": secret_key,
        "bucket": bucket,
        "region": region,
        "prefix": prefix,
        "default_folder": default_folder,
    }


def _sanitize_path_segment(value: str, fallback: str = "default") -> str:
    def normalize_segment(segment: str) -> str:
        segment = segment.strip().lower()
        segment = re.sub(r"[^a-z0-9._-]", "-", segment)
        return segment.strip(".-_")
    
    normalized = normalize_segment(value)
    if normalized:
        return normalized
    
    normalized_fallback = normalize_segment(fallback)
    return normalized_fallback or "default"


def _extract_requester_hint(
    request: Request,
    transfer_process: Optional[TransferProcessStarted] = None,
) -> Optional[str]:
    requester_keys = ["requester", "requesterParticipant", "requestedBy", "participant"]

    # Priority 1: requester-like query params from incoming callback request
    for key in requester_keys:
        value = request.query_params.get(key)
        if value:
            return value

    for header in ["x-requester-participant", "x-requester", "x-participant-id"]:
        value = request.headers.get(header)
        if value:
            return value

    # Priority 2: requester from callback uri embedded in transfer payload
    # (some connector setups may not forward original query params to request)
    if transfer_process:
        for callback in transfer_process.payload.callback_addresses:
            if not callback.uri:
                continue

            callback_query = dict(parse_qsl(urlparse(callback.uri).query))
            for key in requester_keys:
                value = callback_query.get(key)
                if value:
                    return value

    # Priority 3: explicit folder override
    folder_override = request.query_params.get("folder")
    if folder_override:
        return folder_override

    return None


def _filter_proxy_query_params(request: Request) -> List[tuple[str, str]]:
    return [
        (key, value)
        for key, value in request.query_params.multi_items()
        if key.lower() not in INTERNAL_QUERY_PARAM_KEYS
    ]


def _resolve_requester_folder(
    transfer_process: TransferProcessStarted,
    s3_config: dict,
    requester_hint: Optional[str] = None,
) -> str:
    configured_default_folder = s3_config.get("default_folder") or "default"

    if requester_hint:
        return _sanitize_path_segment(requester_hint, fallback=configured_default_folder)

    return _sanitize_path_segment(configured_default_folder, fallback="default")


@app.post("/edr-endpoint/{proxy_path:path}")
@app.post("/edr-endpoint")
async def edr_endpoint(
    request: Request,
    proxy_path: str = "",
):
    logger.info(request)
    logger.info(proxy_path)
    logger.info("Entering edr endpoint")

    proxy_query_params = _filter_proxy_query_params(request)

    logger.info(proxy_query_params)

    # Parse the request body as JSON
    try:
        request_body = await request.json()
        transfer_process = TransferProcessStarted(**request_body)
        logger.info(request_body)
    except Exception as e:
        logger.error("Error parsing request body: %s", str(e))
        raise HTTPException(status_code=422, detail="Invalid request body")

    requester_hint = _extract_requester_hint(request, transfer_process)

    s3_config = get_s3_config()
    logger.info({k: ("***" if "key" in k else v) for k, v in s3_config.items()})
    if not s3_config["endpoint_url"]:
        raise HTTPException(status_code=500, detail="S3 endpoint is not configured (S3_ENDPOINT_URL or STORAGE_ENDPOINT)")
    if not s3_config["access_key"] or not s3_config["secret_key"]:
        raise HTTPException(status_code=500, detail="S3 credentials are not configured (S3_ACCESS_KEY/S3_SECRET_KEY or STORAGE_ACCESS_KEY/STORAGE_SECRET_KEY)")

    s3_client = boto3.client(
        "s3",
        endpoint_url=s3_config["endpoint_url"],
        aws_access_key_id=s3_config["access_key"],
        aws_secret_access_key=s3_config["secret_key"],
        region_name=s3_config["region"],
        config=Config(signature_version="s3v4"),
    )

    response = await get_asset_from_provider(transfer_process, proxy_path, proxy_query_params)

    asset_id = transfer_process.payload.asset_id

    requester_folder = _resolve_requester_folder(transfer_process, s3_config, requester_hint)
    upload_asset_to_storage(s3_client, s3_config, response, asset_id, requester_folder)

    return JSONResponse(content={"status": "success"}, status_code=200)


async def get_asset_from_provider(transfer_process: TransferProcessStarted, proxy_path: str, proxy_query_params: List[tuple]):
    properties = transfer_process.payload.data_address.properties
    endpoint = properties.endpoint
    auth_type = properties.auth_type
    auth_code = properties.authorization

    if not endpoint or not auth_type or not auth_code``:
        logger.error(f"Missing endpoint, auth_type or auth_code. endpoint={endpoint}, auth_type={auth_type}, auth_code={auth_code}")
        return JSONResponse(content={"error": "Missing or invalid endpoint, authKey or authCode parameters."}, status_code=400)

    if proxy_path is not None and proxy_path:
        endpoint = f"{endpoint}/{proxy_path}"

    if proxy_query_params:
        endpoint = f"{endpoint}?{urlencode(proxy_query_params, doseq=True)}"

    logger.info(f"Fetching asset from provider: {endpoint}")
    headers = {"Authorization": auth_code}
    logger.info(f"Headers: {headers}")

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=headers)
        logger.info(f"Response status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
        return response


def upload_asset_to_storage(s3_client, s3_config : dict, response: Response, asset_id: str, requester_folder: str):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Priority 1: Use Content-Type header from response (excluding application/octet-stream)
    content_type_header = response.headers.get("content-type")
    content_type = content_type_header if (content_type_header and content_type_header != "application/octet-stream") else None
    
    # Priority 2: Try file type detection
    if not content_type:
        kind = filetype.guess(response.content)
        content_type = kind.mime if kind else None
    
    # Priority 3: Fallback to application/json
    if not content_type:
        content_type = "application/json"
    
    # Get file extension from mime type
    _ext = mimetypes.guess_extension(content_type)
    if not _ext:
        # Fallback extension based on content type
        if "json" in content_type:
            _ext = ".json"
        elif "csv" in content_type:
            _ext = ".csv"
        elif "pdf" in content_type:
            _ext = ".pdf"
        elif "html" in content_type:
            _ext = ".html"
        elif "xml" in content_type:
            _ext = ".xml"
        elif "text" in content_type:
            _ext = ".txt"
        else:
            _ext = ".bin"

    logger.info(f"Content-Type: {content_type}, Extension: {_ext}")

    participant_folder = _sanitize_path_segment(
        requester_folder,
        fallback=s3_config.get("default_folder") or "default",
    )
    filename = f"{asset_id}-{timestamp}{_ext}"
    object_key = posixpath.join(participant_folder, filename)

    logger.info(f"Uploading to S3: bucket={s3_config['bucket']}, key={object_key}, content_type={content_type}")

    writable_content = io.BytesIO(response.content)

    bucket = s3_config["bucket"]
    ensure_bucket_exists(s3_client, bucket)

    s3_client.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=writable_content.getvalue(),
        ContentType=content_type,
    )
    
    logger.info(f"Successfully uploaded {filename} to S3")


def ensure_bucket_exists(client, bucket_name: str) -> None:
    try:
        client.head_bucket(Bucket=bucket_name)
        return
    except ClientError as exc:
        error_code = (exc.response.get("Error") or {}).get("Code")
        if error_code not in {"404", "NoSuchBucket", "NotFound"}:
            raise

    try:
        client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except ClientError as exc:
        error_code = (exc.response.get("Error") or {}).get("Code")
        if error_code in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
            return
        raise


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    uvicorn.run("app:app", host=IP, port=PORT, reload=True)
