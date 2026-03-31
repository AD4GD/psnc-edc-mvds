from __future__ import annotations

from typing import Annotated

from api.core.logging_config import setup_logging
from api.models.dto.responses import SimpleMessageResponse, VCResponse
from api.services.app import vc_saver_service
from api.services.helper import require_dsh_api_key
from fastapi import APIRouter, Body, Depends, status
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
    "/issue",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Issue VCs for a participant and register in federated catalog",
    dependencies=[Depends(require_dsh_api_key)],
)
async def issue_vc(body: Annotated[InsertVcRequest, Body()]):
    """
    Issue Verifiable Credentials for a participant and add them as a target
    node in the Federated Catalog. Identity Hub participant context creation
    and STS secret storage are handled externally by the init-dataspace script.

    Requires a valid x-api-key header.
    """
    await vc_saver_service.issue_and_store_vcs(body)
    await federated_catalog_service.create_target_node(body.connector_did, body.connector_dsp_url)
    return None