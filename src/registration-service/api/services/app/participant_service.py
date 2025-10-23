import logging

from fastapi import HTTPException, status
from api.models.dto.responses import ParticipantResponse
from api.models.dto.requests import ParticipantCreateRequest
from api.services.clients import async_postgres_service, keycloak_service

logger = logging.getLogger(__name__)


class ParticipantService:
    """ Service for interacting with Participant-related operations. """

    def __init__(self):
        pass

    async def register_participant(self, request : ParticipantCreateRequest, token : str) -> ParticipantResponse:
        """ Register a new participant with the provided information. """
        # TODO validate admin token
        # TODO check content of request
        try:
            participant = await async_postgres_service.create_participant({
                "did": request.did,
                "protocol_url": str(request.protocol_url),
                "location_id": request.location_id,
            })
            # TODO add logic to add "admin" account for this participant - UserService.create_user
            return ParticipantResponse(
                id=str(participant.id),
                did=participant.did,
                name=participant.name,
                protocol_url=participant.protocol_url,
                created_at=participant.created_at.isoformat() if participant.created_at else None,
            )
        except Exception as e:
            logger.exception("Failed to create participant")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    async def get_participant(self, participant_id: str, token : str) -> ParticipantResponse: 
        try:
            payload = keycloak_service._decode_jwt_payload(token)
            if not (keycloak_service.token_has_realm_role(token, "admin") or keycloak_service.authorized_for_participant(token, participant_id)):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        except HTTPException:
            raise
        except Exception:
            # fallback to introspection
            try:
                keycloak_service.introspect_token(token)
            except Exception:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        participant = await async_postgres_service.get_participant(participant_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        return ParticipantResponse(
            id=str(participant.id),
            did=participant.did,
            protocol_url=participant.protocol_url,
            location_id=str(participant.location_id) if participant.location_id else None,
            created_at=participant.created_at.isoformat() if participant.created_at else None,
            updated_at=participant.updated_at.isoformat() if participant.updated_at else None,
        )
    
    async def delete_participant(self, participant_id: str, token : str) -> None:
        # TODO check if auth is ok
        # TODO allow delete by did
        try:
            payload = keycloak_service._decode_jwt_payload(token)
            if not (keycloak_service.token_has_realm_role(token, "admin") or keycloak_service.authorized_for_participant(token, participant_id)):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        except HTTPException:
            raise
        except Exception:
            # fallback to introspection
            try:
                keycloak_service.introspect_token(token)
            except Exception: # TODO switch to RS exception
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        try:
            ok = await async_postgres_service.delete_participant(participant_id)
            if not ok:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Delete failed")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to delete participant")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


participant_service = ParticipantService()
