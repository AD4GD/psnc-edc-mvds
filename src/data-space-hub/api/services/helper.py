import asyncio
import base64
import hashlib
import json
from typing import Any, Dict, Optional
from uuid import uuid4

from api.exceptions.registration_service_exceptions import UnauthorizedException
from api.services.clients import keycloak_service, vault_service
from fastapi import Depends, Header


# ----- dependencies / helpers -----
def get_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract Bearer token from Authorization header or raise 401."""
    if not authorization:
        raise UnauthorizedException(message="Missing Authorization header", action="access protected resource")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(message="Missing Authorization header", action="access protected resource")
    return parts[1]


async def require_admin_token(token: str = Depends(get_bearer_token)):
    """Dependency to require Keycloak admin role (raises 403 on insufficient privileges)."""
    try:
        keycloak_service.require_admin(token)
    except ValueError as exc:
        raise UnauthorizedException(message=str(exc), action="require admin role")
    return token


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def b64url_no_padding(b: bytes) -> str:
    s = base64.urlsafe_b64encode(b).decode()
    return s.rstrip("=")


async def sign_jwt_with_vault(payload: Dict[str, Any], key_name: str, alg: str = "RS256") -> str:
    """
    Async wrapper that creates compact JWT where signature is produced by Vault Transit.
    Uses vault_service.sign_bytes via asyncio.to_thread to avoid blocking the event loop.
    """
    header = {"alg": alg, "typ": "JWT"}
    header_b = json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload_b = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    header_b64 = b64url_no_padding(header_b)
    payload_b64 = b64url_no_padding(payload_b)
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    # call vault sign in thread
    sig_raw = await asyncio.to_thread(vault_service.sign_data, key_name, data=signing_input)

    try:
        sig_base64 = sig_raw.split(":")[-1]
    except AttributeError:
        sig_base64 = sig_raw

    sig_bytes = base64.b64decode(sig_base64)
    sig_b64url = b64url_no_padding(sig_bytes)
    jwt = f"{header_b64}.{payload_b64}.{sig_b64url}"
    return jwt


def create_did(name: str) -> str:
    return "_".join(name.split()) + "_" + str(uuid4())
