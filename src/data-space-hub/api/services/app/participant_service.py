from typing import List
from uuid import uuid4

from api.core.logging_config import setup_logging
from api.exceptions.registration_service_exceptions import RecordNotFoundWarning, UnauthorizedException
from api.models.db.registration_request import RegistrationRequest, RegistrationStatus
from api.models.dto.requests import ParticipantCreateRequest, ParticipantUpdateRequest
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse
from api.services.clients import EmailService, async_postgres_service, keycloak_service
from api.services.helper import create_did
from api.templates.email import participant_accepted_template, participant_confirm_email_template
from api.templates.template_filler import render_jinja_template
from fastapi import HTTPException, Response, status
from fastapi.encoders import jsonable_encoder

logger = setup_logging()


class ParticipantService:
    """Service for interacting with Participant-related operations."""

    def __init__(self):
        pass

    @classmethod
    async def start_participant_registration(cls, request: ParticipantCreateRequest) -> SimpleMessageResponse:
        """
        Start participant registration process.
        Participant sends a request with a form, it is then saved to db into registration_request and email is sent.
        """
        # try:
        payload = {
            "id": uuid4(),
            "status": RegistrationStatus.REQUESTED.value,
            "request_form": jsonable_encoder(request),
            "error_detail": "",  # Test for some error details
            "email_confirmed": False,
        }
        rr = await async_postgres_service.create_registration_request(payload)
        logger.info(f"Created new registration - {rr.id}")

        email_response = EmailService.send_email(
            recipients=[request.email],
            subject="Confirm your email",
            body=render_jinja_template(
                participant_confirm_email_template,
                {"participant_name": request.full_name, "confirmation_link": "https://facebook.com"},
            ),
            body_type="html",
        )
        logger.info(email_response)
        # TODO after participant admin email confirmation - send email to DS admin
        return SimpleMessageResponse(message="Everything OK")  # Make correct response

    @classmethod
    async def register_participant(cls, reg_id) -> ParticipantResponse:
        """Register a new participant with the provided information."""
        # TODO check content of request
        reg_req: RegistrationRequest = await async_postgres_service.get_registration_request(reg_id)
        form: ParticipantCreateRequest = reg_req.request_form

        location = await async_postgres_service.create_location(form["location"])
        participant = await async_postgres_service.create_participant(
            {
                "id": uuid4(),
                "did": create_did(form["name"]),  # or full_name
                "name": form["name"],
                "full_name": form["full_name"],
                "protocol_url": form["protocol_url"],
                "ums_url": form["ums_url"],
                "location_id": location.id,
                "VAT_number": form["VAT_number"],
                "email": form["email"],
            }
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
            raise RecordNotFoundWarning(message="No participants found", record_type="participant list")
        return participants

    @classmethod
    async def get_participant(cls, token: str, response: Response, participant_id: str = None, participant_did: str = None):
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
        if participant_id:
            participant = await async_postgres_service.get_participant(participant_id)
        elif participant_did:
            participant = await async_postgres_service.get_participant_by_did(participant_did)
        if not participant:
            raise RecordNotFoundWarning(message="Participant not found", record_type="participant", record_id=str(participant_id) or participant_did)
        return participant.to_dict()

    @classmethod
    async def update_participant(cls, token: str, participant_id: str, participant: ParticipantUpdateRequest) -> SimpleMessageResponse:
        # TODO all the logic for this function
        return SimpleMessageResponse(message="Participant has been updated")

    @classmethod
    async def delete_participant(cls, token: str, participant_id: str = None, participant_did: str = None) -> None:
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
            ok = await async_postgres_service.delete_participant(p_id=participant_id, did=participant_did)

            if not ok:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Delete failed")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to delete participant")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


participant_service = ParticipantService()
