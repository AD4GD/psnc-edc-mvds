from typing import Annotated, List
from uuid import UUID

from api.core.logging_config import setup_logging
from api.models.db.registration_request import RegistrationStatus
from api.models.dto.requests import ParticipantCreateRequest
from api.models.dto.responses import RegistrationRequestResponse, SimpleMessageResponse
from api.services.app import participant_service, registration_service

# from api.services.helper import get_bearer_token, require_admin_token
from fastapi import APIRouter, Body, Response, status  # , Depends

logger = setup_logging()
router = APIRouter(prefix="/registration/request", tags=["Registration"])


@router.get(
    path="",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
)
async def test_registration():
    """
    Create a new participant record.
    Requires an admin Keycloak token.
    """
    return SimpleMessageResponse(message="Hello there")


@router.post(
    "",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Start participant registration",
)
async def start_registration(req: Annotated[ParticipantCreateRequest, Body()]):
    """
    1. Participant creates infrastructure and run all required services.
    2. Participant's admin send request and waits for Data Space Hub's admin for accept
    """
    return await participant_service.start_participant_registration(req)


@router.get("/count", response_model=int, status_code=status.HTTP_200_OK, summary="Get registration request count")
async def get_participants_count():  # token: str = Depends(get_bearer_token))
    return await registration_service.get_registration_request_count("token")


@router.get(
    "/list",
    response_model=List[RegistrationRequestResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all registration requests",
    responses={status.HTTP_204_NO_CONTENT: {"message": "No data to display"}},
)
# Middleware for checking token and a role
async def get_all_registrations(response: Response, offset : int = 0, limit : int | None = None):  # , token: str = Depends(require_admin_token)):
    """Accept participant registration"""
    return await registration_service.get_all_regitrations_requests("token", response, offset, limit)


@router.get(
    "/{request_id}",
    response_model=RegistrationRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get registration request",
    responses={status.HTTP_204_NO_CONTENT: {"message": "No data to display"}},
)
# Middleware for checking token and a role
async def get_registration(response: Response, request_id: UUID):  # , token: str = Depends(require_admin_token)):
    """Get registration request"""
    return await registration_service.get_registration_request("token", response, request_id)


@router.put(
    "/{request_id}/approve",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Accept participant registrattion",
)
# Middleware for checking token and a role
async def accept_registration(request_id: UUID):  # , token: str = Depends(require_admin_token)):
    """Accept participant registration"""
    return await registration_service.update_registration_status("token", request_id, RegistrationStatus.APPROVED)


@router.put(
    "/{request_id}/reject",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Reject participant registration",
)
async def reject_registration(request_id: UUID):  # , token: str = Depends(require_admin_token)):
    """Reject participant registration"""
    return await registration_service.update_registration_status("token", request_id, RegistrationStatus.REJECTED)


@router.put(
    "/{request_id}/onboard",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Onboard participant",
)
async def onboard_registration(request_id: UUID):  # , token: str = Depends(require_admin_token)):
    """Onboard participant registration"""
    return await registration_service.update_registration_status("token", request_id, RegistrationStatus.ONBOARDED)


@router.delete(
    "/{request_id}",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete participant",
)
async def delete_registration(request_id: UUID):  # , token: str = Depends(require_admin_token)):
    """Delete participant registration"""
    return await registration_service.delete_registration_request("token", request_id)
