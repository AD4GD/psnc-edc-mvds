from __future__ import annotations
from typing import Annotated

from api.core.logging_config import setup_logging
from api.core.settings import ProjectSettings
from api.models.dto.responses import SimpleMessageResponse, VCResponse
from api.models.dto.requests import UserInfoVCRequest
from api.services.app import vc_service
from fastapi import APIRouter, Body, status

logger = setup_logging()
router = APIRouter(prefix="/verifiable-credentials", tags=["Verifiable Credentials"])


@router.get(
    f"",
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
    "",
    response_model=VCResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve VC for users"
)
def retrieve_vc(body: Annotated[UserInfoVCRequest, Body()]):
    """ Main endpoint that is responsible for handling requests from User Management System and generating Verifiable Credentials for users of connector """
    return vc_service.create_vc(body)