import logging
from fastapi import APIRouter, status

from api.models.dto.requests import UserRegistrationRequest
from api.models.dto.responses import UserRegistrationResponse
from api.services.app import user_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["registration", "register"])


@router.post(
    "/users/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user via connector token",
)
async def register_user(req: UserRegistrationRequest):
    """
    Full registration flow for a single user triggered by a connector:
      1. Store registration_request (hashed token) in DB for audit.
      2. Construct VC payload and sign it using Vault (transit key).
      3. Store issued_credential metadata in DB (hash + pointer).
      4. POST VC back to connector callback URL together with original connector token.
    Security:
      - This endpoint expects the connector to present a short-lived connector_token in the request body;
        the RS should validate it (e.g. compare hash against previously provisioned token or validate signature).
      - For demo flow the token is stored as a SHA256 hash (do not store plaintext tokens in DB).
    """
    print(req)
    # return UserRegistrationResponse(
    #     credential_id=("abcd-uuid"),
    #     credential_hash=sha256_hex(b"dummy-vc"),
    #     issued_at=str(1234567890),
    #     issued_to=str("consumer_user"),
    #     storage_ref=(f"connector://participant.did/vc/vc_hash"),
    # )

    user_service.create_user(req)
