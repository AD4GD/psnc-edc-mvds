import logging

from typing import List
from fastapi import APIRouter, Depends, status
from api.services.app import participant_service
from api.models.dto.requests import ParticipantCreateRequest
from api.models.dto.responses import ParticipantResponse
from api.services.helper import get_bearer_token, require_admin_token


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/participants", tags=["participant", "manage participant"])


@router.get(
    "/list",
    response_model=List[ParticipantResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Get list of all participants (admin)",
)
async def get_all_participants():#token: str = Depends(require_admin_token)):
    """
    Create a new participant record.
    Requires an admin Keycloak token.
    """
    return await participant_service.get_all_participants()


@router.get(
    "/{participant_id}",
    response_model=ParticipantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get participant by id (admin or authorized)",
)
async def get_participant(participant_id: str, token: str = Depends(get_bearer_token)):
    """
    Return participant. Admins allowed; non-admins allowed only if keycloak_service.authorized_for_participant returns True.
    """
    return await participant_service.delete_participant(participant_id, token)


@router.get(
    "/did/{participant_did}",
    response_model=ParticipantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get participant by id (admin or authorized)",
)
async def get_participant_by_did(participant_did: str, token: str = Depends(get_bearer_token)):
    """
    Return participant. Admins allowed; non-admins allowed only if keycloak_service.authorized_for_participant returns True.
    """
    return await participant_service.get_participant(participant_did)


@router.delete(
    "/{participant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete participant (admin)",
)
async def delete_participant(participant_id: str, token: str = Depends(require_admin_token)):
    return await participant_service.delete_participant(participant_id, token)
