from typing import Annotated, List, Optional
from uuid import UUID

from api.core.logging_config import setup_logging
from api.models.dto.requests import RegistrationCreateRequest
from api.models.dto.responses import RegistrationRequestResponse, SimpleMessageResponse
from api.services.app import registration_service
from api.models.db.registration_request import RegistrationStatus
from api.services.helper import require_admin_token
from fastapi import APIRouter, Body, Depends, Path, Query, Response, status
from fastapi.responses import JSONResponse

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
async def start_registration(req: Annotated[RegistrationCreateRequest, Body()]):
    """
    Public endpoint. Company employee submits registration with company info.
    An email confirmation link is sent.
    """
    return await registration_service.start_participant_registration(req)


@router.get("/count", response_model=int, status_code=status.HTTP_200_OK, summary="Get registration request count")
async def get_participants_count(token: str = Depends(require_admin_token)):
    return await registration_service.get_registration_request_count(token)


@router.get(
    "/list",
    response_model=List[RegistrationRequestResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all registration requests",
    responses={status.HTTP_204_NO_CONTENT: {"message": "No data to display"}},
)
async def get_all_registrations(response: Response, offset: int = 0, limit: int | None = None, token: str = Depends(require_admin_token)):
    """List all registration requests. Admin only."""
    return await registration_service.get_all_regitrations_requests(token, response, offset, limit)


@router.get(
    "/{request_id}",
    response_model=RegistrationRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get registration request",
    responses={status.HTTP_204_NO_CONTENT: {"message": "No data to display"}},
)
async def get_registration(response: Response, request_id: UUID, token: str = Depends(require_admin_token)):
    """Get registration request. Admin only."""
    return await registration_service.get_registration_request(token, response, request_id)

@router.get(
    "/{request_id}/email-confirm",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Confirm user email",
)
async def confirm_email(
    request_id: UUID = Path(..., description="Registration request UUID"),
    token: str = Query(..., description="Email confirmation token"),
):
    is_valid = await registration_service.assert_registration_token(request_id, token)

    if is_valid is False:
        return JSONResponse(status_code=403, content={"message": "Wrong or expired confirmation token"})

    await registration_service.confirm_email(request_id)

    return SimpleMessageResponse(message="Email has been confirmed")

@router.put(
    "/{request_id}/approve",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Accept participant registration",
)
async def accept_registration(request_id: UUID, token: str = Depends(require_admin_token)):
    """Approve a registration request. Admin only. Creates Keycloak user and participant."""
    return await registration_service.update_registration_status(request_id, RegistrationStatus.APPROVED)

@router.put(
    "/{request_id}/reject",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Reject participant registration",
)
async def reject_registration(
    request_id: UUID,
    reason: Optional[str] = Body(None, embed=True),
    token: str = Depends(require_admin_token),
):
    """Reject a registration request. Admin only. Optionally provide a reason."""
    return await registration_service.update_registration_status(request_id, RegistrationStatus.REJECTED, reject_reason=reason or "")

@router.put(
    "/{request_id}/retry",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry failed onboarding",
)
async def retry_onboarding(request_id: UUID, token: str = Depends(require_admin_token)):
    """Retry onboarding for a registration that previously failed (e.g. Keycloak error). Admin only."""
    return await registration_service.retry_onboarding(request_id)

@router.delete(
    "/{request_id}",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete participant",
)
async def delete_registration(request_id: UUID, token: str = Depends(require_admin_token)):
    """Delete participant registration. Admin only."""
    return await registration_service.delete_registration_request(token, request_id)
