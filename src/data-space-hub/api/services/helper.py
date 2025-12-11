import base64
import hashlib
from typing import Optional
from uuid import uuid4

from api.exceptions.registration_service_exceptions import UnauthorizedException
from api.services.clients import keycloak_service
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


def create_did(name: str) -> str:
    return "_".join(name.split()) + "_" + str(uuid4())


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


# async def make_jwt(payload: Dict, key_name: str, verification_method: str) -> str:
#     """
#     Creates a signed JWT (JWS) using Vault for signing.
#     Handles Vault's specific response format and ensures URL-safe Base64 encoding.
#     """
#     # 1. Prepare Header
#     # EdDSA is standard for Ed25519 keys. If using RSA, change to RS256.
#     header = {"alg": "EdDSA", "typ": "JWT", "kid": verification_method}

#     header_b64 = b64url(json.dumps(header, separators=(",", ":")).encode())
#     payload_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode())
#     signing_input = f"{header_b64}.{payload_b64}".encode()

#     vault_response = vault_service.sign_data(key_name, signing_input)
#     # await asyncio.to_thread(
#     #     vault_service.sign_data,
#     #     key_name,
#     #     signing_input
#     #     # hash_algorithm=HashAlgorithmEnum.SHA2_256 # Uncomment if using RSA/EC keys
#     # )

#     # 3. Parse Vault Response (format: "vault:v1:base64_signature")
#     try:
#         # Extract the base64 part after the last colon
#         print(vault_response)
#         sig_base64_std = vault_response.split(":")[-1]
#     except AttributeError:
#         # Fallback if Vault returns raw bytes or unexpected format
#         sig_base64_std = vault_response

#     # 4. Convert Standard Base64 (Vault) -> Raw Bytes -> URL-Safe Base64 (JWT)
#     sig_b64url = b64url(base64.b64decode(sig_base64_std))
#     # sig_b64url = b64url(sig_bytes)
#     print(sig_base64_std)
#     print(sig_b64url)

#     return f"{header_b64}.{payload_b64}.{sig_b64url}"
