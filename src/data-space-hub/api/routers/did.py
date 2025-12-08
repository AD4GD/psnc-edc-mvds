from __future__ import annotations

from api.core.logging_config import setup_logging
from api.models.dto.responses import DIDResponse
from api.services.clients.vault_service import vault_service
from fastapi import APIRouter, status

logger = setup_logging()
router = APIRouter(tags=["Public key"])


@router.get(
    "/.well-known/did.json",
    response_model=DIDResponse,
    status_code=status.HTTP_200_OK,
    summary="Download issuer public key",
)
def did_document():
    """
    Retreive DID Document with public key for verifying signatures of issued Verifiable Credentials.
    """
    return vault_service.prepare_did_document()
