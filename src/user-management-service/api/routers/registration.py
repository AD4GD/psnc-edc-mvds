from typing import Annotated, List
from uuid import UUID

from api.core.logging_config import setup_logging
from api.models.db.registration_request import RegistrationStatus
from api.models.dto.requests import UserCreateRequest
from api.models.dto.responses import RegistrationRequestResponse, SimpleMessageResponse
from api.services.app import participant_service, registration_service

# from api.services.helper import get_bearer_token, require_admin_token
from fastapi import APIRouter, Body, Response, status, HTTPException  # , Depends

logger = setup_logging()
router = APIRouter(prefix="/registration/requests", tags=["Registration"])


@router.post(
    "",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Start user registration",
)
async def start_registration(request: Annotated[UserCreateRequest, Body()]):
    return await participant_service.start_participant_registration(request)

@router.get(
    "",
    response_model=List[RegistrationRequestResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all registration requests"
)
async def get_all_registrations(offset : int = 0, limit : int | None = None):
    # should be protected via JWT-signed token
    # auth-related logic
    # token: str = Depends(get_bearer_token))

    registration_requests = await registration_service.get_all_regitrations_requests(offset, limit)
    return registration_requests

@router.get(
    "/count", 
    response_model=int, 
    status_code=status.HTTP_200_OK, 
    summary="Get registration requests count"
)
async def get_requests_count():
    # should be protected via JWT-signed token
    # auth-related logic
    # token: str = Depends(get_bearer_token))

    return await registration_service.get_registration_requests_count()

@router.get(
    "/{request_id}",
    response_model=RegistrationRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get registration request",
    responses={
        404: {
            "description": "Registration request not found",
        }
    },
)
async def get_registration(request_id: UUID):
    # should be protected via JWT-signed token
    # auth-related logic
    # token: str = Depends(require_admin_token))

    registration_request = await registration_service.get_registration_request(request_id)
    logger.info(registration_request)

    if registration_request is None:
        raise HTTPException(status_code=404, detail="Registration request not found")
    
    return registration_request


@router.put(
    "/{request_id}/approve",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Accept participant registrattion",
)
async def accept_registration(request_id: UUID):
    # should be protected via JWT-signed token
    # auth-related logic
    # token: str = Depends(require_admin_token))

    return await registration_service.update_registration_status("token", request_id, RegistrationStatus.APPROVED)


@router.put(
    "/{request_id}/reject",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Reject participant registration",
)
async def reject_registration(request_id: UUID):
    # should be protected via JWT-signed token
    # auth-related logic
    # token: str = Depends(require_admin_token))

    return await registration_service.update_registration_status("token", request_id, RegistrationStatus.REJECTED)


@router.put(
    "/{request_id}/onboard",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Onboard participant",
)
async def onboard_registration(request_id: UUID):
    # should be protected via JWT-signed token
    # auth-related logic
    # token: str = Depends(require_admin_token))

    return await registration_service.update_registration_status("token", request_id, RegistrationStatus.ONBOARDED)


@router.delete(
    "/{request_id}",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete participant",
)
async def delete_registration(request_id: UUID):
    # should be protected via JWT-signed token
    # auth-related logic
    # token: str = Depends(require_admin_token))

    return await registration_service.delete_registration_request("token", request_id)
