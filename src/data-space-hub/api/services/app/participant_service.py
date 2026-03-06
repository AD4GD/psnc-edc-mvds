from typing import List
from uuid import uuid4

from api.core.logging_config import setup_logging
from api.exceptions.registration_service_exceptions import RecordNotFoundException, UnauthorizedException
from api.models.db.registration_request import RegistrationRequest
from api.models.dto.requests import ParticipantCreateRequest, ParticipantUpdateRequest
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse
from api.services.clients import EmailService, async_postgres_service, keycloak_service
from api.templates.email import participant_accepted_template
from api.templates.template_filler import render_jinja_template
from fastapi import HTTPException, status

logger = setup_logging()


class ParticipantService:
    """Service for interacting with Participant-related operations."""

    def __init__(self):
        pass

    @classmethod
    async def register_participant(cls, reg_id) -> ParticipantResponse:
        """Register a new participant with the provided information."""
        # TODO check content of request
        reg_req: RegistrationRequest = await async_postgres_service.get_registration_request(reg_id)
        form: ParticipantCreateRequest = reg_req.request_form

        async with async_postgres_service.atomic() as session:
            form["location"]["id"] = uuid4()
            location = await async_postgres_service.create_location(form["location"], session=session)
            participant = await async_postgres_service.create_participant(
                {
                    "id": uuid4(),
                    "name": form["name"],
                    "full_name": form["full_name"],
                    "data_space_components": form["data_space_components"],
                    "location_id": location.id,
                    "VAT_number": form["VAT_number"],
                    "email": form["email"],
                },
                session=session,
            )

        EmailService.send_email(
            [form["email"]],
            "Data Space - Onboarding",
            render_jinja_template(participant_accepted_template, {"participant_name": form["full_name"]}),
            "html",
        )
        return participant

    @classmethod
    async def get_participants_count(cls, token):
        # TODO auth
        return await async_postgres_service.get_participant_count()

    @classmethod
    async def get_all_participants(cls, token: str, offset: int = 0, limit: int | None = None) -> List[ParticipantResponse]:
        # try:
        #     payload = keycloak_service.decode_jwt_payload(token)
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

        participants = await async_postgres_service.list_participants(offset, limit)
        for i, participant in enumerate(participants):
            participants[i] = participant.to_dict()
        if not participants:
            raise RecordNotFoundException(message="No participants found", status_code=204, record_type="participant list")
        return participants

    @classmethod
    async def get_participant(cls, token: str, participant_id: str):
        # try:
        #     keycloak_service.decode_jwt_payload(token)
        #     if not (
        #         keycloak_service.token_has_realm_role(token, "admin")
        #         or keycloak_service.authorized_for_participant(token, participant_id)
        #     ):
        #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        # except HTTPException:
        #     raise
        # except Exception:
        #     # fallback to introspection
        #     try:
        #         keycloak_service.introspect_token(token)
        #     except Exception:
        #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        participant = None
        participant = await async_postgres_service.get_participant(participant_id)
        if not participant:
            raise RecordNotFoundException(message="Participant not found", status_code=204, record_type="participant", record_id=str(participant_id))
        return participant.to_dict()

    @classmethod
    async def update_participant(cls, token: str, participant_id: str, participant: ParticipantUpdateRequest) -> SimpleMessageResponse:
        # TODO all the logic for this function
        return SimpleMessageResponse(message="Participant has been updated")

    @classmethod
    async def delete_participant(cls, token: str, participant_id: str) -> None:
        # TODO check if auth is ok
        try:
            keycloak_service.decode_jwt_payload(token)
            if not (keycloak_service.token_has_realm_role(token, "admin") or keycloak_service.authorized_for_participant(token, participant_id)):
                raise UnauthorizedException(message="Insufficient permissions", action="delete participant")
        except HTTPException:
            raise
        except Exception:  # pylint: disable=W0718
            # fallback to introspection
            keycloak_service.introspect_token(token)

        try:
            ok = await async_postgres_service.delete_participant(p_id=participant_id)

            if not ok:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Delete failed")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to delete participant")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


participant_service = ParticipantService()
