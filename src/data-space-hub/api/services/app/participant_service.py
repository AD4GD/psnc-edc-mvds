import logging

from typing import List
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse, ErrorResponse
from api.models.dto.requests import ParticipantCreateRequest
from api.services.clients import async_postgres_service, keycloak_service
from api.models.db.registration_request import RegistrationStatus, RegistrationRequest
from api.services.helper import create_did

logger = logging.getLogger(__name__)


class ParticipantService:
    """ Service for interacting with Participant-related operations. """

    def __init__(self):
        pass

    async def start_participant_registration(self, request : ParticipantCreateRequest) -> SimpleMessageResponse:
        """ 
            Start participant registration process. 
            Participant sends a request with a form, it is then saved to db into registration_request and emial is sent.
        """
        try:
            payload = {
                "status" : RegistrationStatus.REQUESTED.value,
                "request_form" : jsonable_encoder(request),
                "error_detail" : "", # Test for some error details
                "email_confirmed" : False
            }
            rr = await async_postgres_service.create_registration_request(payload)
            # TODO send email to participant admin to confirm email
            # TODO after participant admin email confirmation - send email to DS admin
            return SimpleMessageResponse(message='Everything OK') # Make correct response
        except Exception as e:
            return ErrorResponse(e.__str__(), detail='Something occured')


    async def update_participant_registration_status(self, rr_id : str, _status : RegistrationStatus) -> SimpleMessageResponse:
        """ Update participant registration process status. """
        try:
            rr = await async_postgres_service.update_registration_request(rr_id, { "status" : _status })
            if _status == RegistrationStatus.ONBOARDED:
                await self.register_participant(rr_id)
                return SimpleMessageResponse(message="Participant has been onboarded and created in DB")
            return SimpleMessageResponse(message="Registration request updated")
        except Exception as e:
            logger.exception("Failed to update registration status")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
    async def register_participant(self, req_id) -> ParticipantResponse:
        """ Register a new participant with the provided information. """
        # TODO check content of request
        try:
            reg_req : RegistrationRequest = await async_postgres_service.get_registration_request(req_id)
            form : ParticipantCreateRequest = reg_req.request_form
            print(form)
            location = await async_postgres_service.create_location(form["location"])
            participant = await async_postgres_service.create_participant({
                "did" : create_did(form["name"]), # or full_name
                "name" : form["name"],
                "full_name" : form["full_name"],
                "protocol_url" : str(form["protocol_url"]),
                "location_id" : location.id,
                "VAT_number" : form["VAT_number"],
                "email" : form["email"],
            })
            # TODO send email to participant
            return participant 
        #         ParticipantResponse(
        #         id=str(participant.id),
        #         did=participant.did,
        #         name=participant.name,
        #         protocol_url=participant.protocol_url,
        #         created_at=participant.created_at.isoformat() if participant.created_at else None,
        #     )
        except Exception as e:
            logger.exception("Failed to create participant")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    async def get_participant(self, token : str, participant_id: str = None, participant_did : str = None) -> ParticipantResponse: 
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

        participant = None
        if participant_id:
            participant = await async_postgres_service.get_participant(participant_id)
        elif participant_did:
            participant = await async_postgres_service.get_participant_by_did(participant_did)
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
    
    async def get_all_participants(self) -> List[ParticipantResponse]: #, token : str
        # try:
        #     payload = keycloak_service._decode_jwt_payload(token)
        #     if not (keycloak_service.token_has_realm_role(token, "admin")):
        #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        # except HTTPException:
        #     raise
        # except Exception:
        #     # fallback to introspection
        #     try:
        #         keycloak_service.introspect_token(token)
        #     except Exception:
        #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        participants = await async_postgres_service.list_participants(0, None)
        # participants = [ participant.__info_to_json__() for participant in participants]
        for i, participant in enumerate(participants):
            print(participant.location.__info_to_json__())
            participants[i] = participant.__info_to_json__()
            print(participants[i])
            # participant[i]["location"] = participant.location.__info_to_json__() #async_postgres_service.get_location(participant.location_id)
        print(participants)
        if len(participants) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participants not found")
        return participants
    
    async def delete_participant(self, token : str, participant_id: str = None, participant_did: str = None) -> None:
        # TODO check if auth is ok
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
            if participant_id:
                ok = await async_postgres_service.delete_participant(id=participant_id, participant_did=participant_did)

            if not ok:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Delete failed")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to delete participant")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


participant_service = ParticipantService()
