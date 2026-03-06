from __future__ import annotations

from typing import Annotated

from api.core.logging_config import setup_logging
from api.models.dto.requests import InsertVcRequest
from api.models.dto.responses import SimpleMessageResponse, VCResponse
from api.services.app import vc_service
from fastapi import APIRouter, Body, status

logger = setup_logging()
router = APIRouter(prefix="/verifiable-credentials", tags=["Verifiable Credentials"])

@router.post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Allows to create participants and VCs",
)
async def create_vc(body: Annotated[InsertVcRequest, Body()]):
    return await vc_service.create_participant_and_save_vc(body)

@router.put(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Allows to update VCs for the users, useful during issuer's private key rotation",
)
async def update_vc(body: Annotated[InsertVcRequest, Body()]):
    return await vc_service.create_participant_and_save_vc(body)