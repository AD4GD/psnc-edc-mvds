import base64
import hashlib
import json
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Header, status
from api.services.clients import vault_service, keycloak_service


# ----- dependencies / helpers -----
def get_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract Bearer token from Authorization header or raise 401."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    return parts[1]


async def require_admin_token(token: str = Depends(get_bearer_token)):
    """Dependency to require Keycloak admin role (raises 403 on insufficient privileges)."""
    try:
        keycloak_service.require_admin(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return token


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def b64url_no_padding(b: bytes) -> str:
    s = base64.urlsafe_b64encode(b).decode()
    return s.rstrip("=")


async def sign_jwt_with_vault(payload: Dict[str, Any], key_name: str, alg: str = "RS256") -> str:
    """
    Create a compact JWT (header.payload.signature) where signature is produced by Vault Transit.
    Implementation assumes vault_service.sign_bytes(key_name, data_bytes) exists and returns a Vault-style
    signature string like 'vault:v1:BASE64'. We extract the BASE64 part and convert to base64url without padding.
    """
    header = {"alg": alg, "typ": "JWT"}
    header_b = json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload_b = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    header_b64 = b64url_no_padding(header_b)
    payload_b64 = b64url_no_padding(payload_b)
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    # vault_service.sign_bytes should accept raw bytes and return a signature string
    sig_raw = vault_service.sign_bytes(key_name, signing_input)
    # typical Vault signature format: "vault:v1:BASE64"
    try:
        sig_base64 = sig_raw.split(":")[-1]
    except Exception:
        # if signature is already base64, use it
        sig_base64 = sig_raw

    # convert standard base64 to base64url (strip padding)
    sig_bytes = base64.b64decode(sig_base64)
    sig_b64url = b64url_no_padding(sig_bytes)
    jwt = f"{header_b64}.{payload_b64}.{sig_b64url}"
    return jwt
