from typing import Annotated, List, Optional
from uuid import UUID

from api.core.logging_config import setup_logging
from api.models.dto.requests import ParticipantUpdateRequest
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse
from api.services.app import participant_service
from api.services.helper import get_bearer_token, require_admin_token
from fastapi import APIRouter, Body, Depends, Query, status

logger = setup_logging()
router = APIRouter(prefix="/participants", tags=["Participant"])

@router.get(
    "/list",
    response_model=List[ParticipantResponse],
    status_code=status.HTTP_200_OK,
    summary="Get list of all participants (admin)",
    responses={status.HTTP_204_NO_CONTENT: {"message": "No participant found"}},
)
async def get_all_participants(offset: int = 0, limit: int | None = None, token: str = Depends(require_admin_token)):
    """
    List all participants.
    Requires an admin Keycloak token.
    """
    return await participant_service.get_all_participants(token, offset, limit)


@router.get("/count", response_model=int, status_code=status.HTTP_200_OK, summary="Get participants count")
async def get_participants_count(token: str = Depends(require_admin_token)):
    return await participant_service.get_participants_count(token)


@router.delete(
    "/me",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Self-offboard: remove your own organization from the Data Space",
)
async def offboard_self(
    reason: Optional[str] = Query(None, description="Optional reason for leaving"),
    token: str = Depends(get_bearer_token),
):
    """
    Authenticated participant removes their own organization.
    Deletes their Keycloak account, participant record, and sends a confirmation email.
    """
    return await participant_service.offboard_self(token, reason=reason or "")


@router.get(
    "/{participant_id}",
    response_model=ParticipantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get participant by id (admin or authorized)",
    responses={status.HTTP_204_NO_CONTENT: {"message": "No participant found"}},
)
async def get_participant(participant_id: UUID, token: str = Depends(get_bearer_token)):
    """
    Return participant. Admins allowed; non-admins allowed only if authorized for this participant.
    """
    return await participant_service.get_participant(token, participant_id=participant_id)


@router.put(
    "/{participant_id}",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update participant by id (admin or authorized)",
)
async def update_participant(
    participant_id: UUID,
    participant: Annotated[ParticipantUpdateRequest, Body()],
    token: str = Depends(get_bearer_token),
):
    """
    Admins allowed; non-admins allowed only if keycloak_service.authorized_for_participant returns True.
    """
    return await participant_service.update_participant(token, participant_id, participant)


@router.delete(
    "/{participant_id}",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Offboard participant (admin only)",
)
async def delete_participant(
    participant_id: str,
    reason: Optional[str] = Query(None, description="Optional reason for offboarding"),
    token: str = Depends(require_admin_token),
):
    """
    Admin removes a participant from the Data Space.
    Deletes their Keycloak account, participant DB record, and sends an offboarding email.
    """
    return await participant_service.delete_participant(token, participant_id, reason=reason or "")
