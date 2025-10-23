import logging

from fastapi import APIRouter, Depends, status
from api.services.app import participant_service
from api.models.dto.requests import ParticipantCreateRequest
from api.models.dto.responses import ParticipantResponse
from api.services.helper import get_bearer_token, require_admin_token


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/participant", tags=["registration", "register"])


@router.post(
    "/participants",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create participant (admin)",
)
async def create_participant(req: ParticipantCreateRequest, token: str = Depends(require_admin_token)):
    """
    Create a new participant record.
    Requires an admin Keycloak token.
    """
    return participant_service.register_participant(req, token)
    

@router.get(
    "/participants/{participant_id}",
    response_model=ParticipantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get participant by id (admin or authorized)",
)
async def get_participant(participant_id: str, token: str = Depends(get_bearer_token)):
    """
    Return participant. Admins allowed; non-admins allowed only if keycloak_service.authorized_for_participant returns True.
    """
    return participant_service.delete_participant(participant_id, token)


@router.delete(
    "/participants/{participant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete participant (admin)",
)
async def delete_participant(participant_id: str, token: str = Depends(require_admin_token)):
    return participant_service.delete_participant(participant_id, token)
