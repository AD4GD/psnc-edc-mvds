import logging

from api.models.dto.requests import UserRegistrationRequest

# from api.models.dto.responses import SimpleMessageResponse, UserRegistrationResponse
from api.core.logging_config import setup_logging
from api.services.app import user_service
from fastapi import APIRouter, status

logger = setup_logging()
router = APIRouter(prefix="/users", tags=["user"])


@router.post(
    "/register",
    # response_model=SimpleMessageResponse, # UserRegistrationResponse
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

    return await user_service.create_user(req)
