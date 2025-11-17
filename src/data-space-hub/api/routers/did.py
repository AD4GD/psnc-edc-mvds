from __future__ import annotations

from api.core.logging_config import setup_logging
from api.models.dto.responses import SimpleMessageResponse
from fastapi import APIRouter, status

logger = setup_logging()
router = APIRouter(tags=["Public key"])


@router.get(
    f".well-known/did.json",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Download issuer public key",
)
def test_endpoint():
    # TODO implement actual public key retrieval
    """
    Test endpoint with various stages
    """
    return SimpleMessageResponse(message="Test endpoint reached successfully")
