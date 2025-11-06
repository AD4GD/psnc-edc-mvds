import logging

from fastapi import APIRouter, Depends, status
from api.services.app import participant_service
from api.models.dto.requests import ParticipantCreateRequest
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse
from api.services.helper import get_bearer_token, require_admin_token
from api.models.db.registration_request import RegistrationStatus


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/register", tags=["registration", "register"])


@router.get(
    path="",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Start participant registration",
)
async def test_registration():
    """
    Create a new participant record.
    Requires an admin Keycloak token.
    """
    return SimpleMessageResponse(message='Hello there')


@router.post(
    "/participant/request",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Start participant registration",
)
async def start_registration(req: ParticipantCreateRequest):
    """
    Create a new participant record.
    Requires an admin Keycloak token.
    """
    # print(req)
    return await participant_service.start_participant_registration(req)


@router.post(
    "/participant/request/{request_id}/accept",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Accept participant registrattion",
)
# Middleware for checking token and a role
async def accept_registration(request_id : str): #, token: str = Depends(require_admin_token)):
    """ Accept participant registration """
    return await participant_service.update_participant_registration_status(request_id, RegistrationStatus.APPROVED)


@router.post(
    "/participant/request/{request_id}/reject",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Reject participant registration",
)
async def reject_registration(request_id: str):#, token: str = Depends(require_admin_token)):
    """ Reject participant registration """
    return await participant_service.update_participant_registration_status(request_id, RegistrationStatus.REJECTED)


@router.post(
    "/participant/request/{request_id}/onboard",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Onboard participant",
)
async def onboard_registration(request_id: str):#, token: str = Depends(require_admin_token)):
    """ Reject participant registration """
    return await participant_service.update_participant_registration_status(request_id, RegistrationStatus.ONBOARDED)
