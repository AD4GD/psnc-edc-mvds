from typing import Annotated, List
from uuid import UUID

from api.core.logging_config import setup_logging
from api.models.dto.requests import ParticipantUpdateRequest
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse
from api.services.app import participant_service
from api.services.helper import get_bearer_token  # , require_admin_token
from fastapi import APIRouter, Body, Depends, status

logger = setup_logging()
router = APIRouter(prefix="/participants", tags=["Participant"])

@router.get(
    "/list",
    response_model=List[ParticipantResponse],
    status_code=status.HTTP_200_OK,
    summary="Get list of all participants (admin)",
    responses={status.HTTP_204_NO_CONTENT: {"message": "No participant found"}},
)
async def get_all_participants(offset: int = 0, limit: int | None = None):  # token: str,  = Depends(require_admin_token)):
    """
    Create a new participant record.
    Requires an admin Keycloak token.
    """
    return await participant_service.get_all_participants("", offset, limit)


@router.get("/count", response_model=int, status_code=status.HTTP_200_OK, summary="Get participants count")
async def get_participants_count():  # token: str = Depends(get_bearer_token))
    return await participant_service.get_participants_count("token")


@router.get(
    "/{participant_id}",
    response_model=ParticipantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get participant by id (admin or authorized)",
    responses={status.HTTP_204_NO_CONTENT: {"message": "No participant found"}},
)
async def get_participant(participant_id: UUID):  # , token: str = Depends(get_bearer_token)):
    """
    Return participant. Admins allowed; non-admins allowed only if keycloak_service.authorized_for_participant returns True.
    """
    return await participant_service.get_participant("token", participant_id=participant_id)


# @router.get(
#     "/did/{participant_did}",
#     response_model=ParticipantResponse,
#     status_code=status.HTTP_200_OK,
#     summary="Get participant by id (admin or authorized)",
# )
# async def get_participant_by_did(participant_did: str):  # , token: str = Depends(get_bearer_token)):
#     """
#     Return participant. Admins allowed; non-admins allowed only if keycloak_service.authorized_for_participant returns True.
#     """
#     return await participant_service.get_participant("token", participant_did=participant_did)


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
    status_code=status.HTTP_200_OK,
    summary="Delete participant (admin or authorized)",
)
async def delete_participant(participant_id: str):  # , token: str = Depends(require_admin_token)):
    return await participant_service.delete_participant(participant_id, "token")
