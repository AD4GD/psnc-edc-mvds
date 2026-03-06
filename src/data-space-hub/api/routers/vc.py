from __future__ import annotations

from typing import Annotated

from api.core.logging_config import setup_logging
from api.models.dto.responses import SimpleMessageResponse, VCResponse
from api.services.app import vc_saver_service
from fastapi import APIRouter, Body, status
from api.models.dto.requests import InsertVcRequest
from api.services.clients import federated_catalog_service

logger = setup_logging()
router = APIRouter(prefix="/verifiable-credentials", tags=["Verifiable Credentials"])


@router.get(
    "",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Allow participant to generate new VCs for its users when keys rotate",
)
def test_endpoint():
    # TODO implement actual public key retrieval
    """
    Test endpoint with various stages
    """
    return SimpleMessageResponse(message="Test endpoint reached successfully")

@router.post(
    "/test",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Test save",
)
async def save_vc(body: Annotated[InsertVcRequest, Body()]):
    result = await vc_saver_service.create_participant_and_save_vc(body)
    await federated_catalog_service.create_target_node(body.connector_did, body.connector_dsp_url)
    return result