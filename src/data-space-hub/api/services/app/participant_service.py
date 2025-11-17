from typing import List
from uuid import uuid4

from api.core.logging_config import setup_logging
from api.models.db.registration_request import RegistrationRequest, RegistrationStatus
from api.models.dto.requests import ParticipantCreateRequest, ParticipantUpdateRequest
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse
from api.services.clients import EmailService, async_postgres_service, keycloak_service
from api.services.helper import create_did
from api.templates.email import participant_accepted_template, participant_confirm_email_template
from api.templates.template_filler import render_jinja_template
from fastapi import HTTPException, Response, status
from fastapi.encoders import jsonable_encoder

# from .registration_service import registration_service

logger = setup_logging()


class ParticipantService:
    """Service for interacting with Participant-related operations."""

    def __init__(self):
        pass

    async def start_participant_registration(self, request: ParticipantCreateRequest) -> SimpleMessageResponse:
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

    async def register_participant(self, reg_id) -> ParticipantResponse:
        """Register a new participant with the provided information."""
        # TODO check content of request
        reg_req: RegistrationRequest = await async_postgres_service.get_registration_request(reg_id)
        form: ParticipantCreateRequest = reg_req.request_form

        location = await async_postgres_service.create_location(form["location"])
        participant = await async_postgres_service.create_participant(
            {
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

    async def get_participant(
        self, token: str, response: Response, participant_id: str = None, participant_did: str = None
    ):
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
            # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
            response.status_code = status.HTTP_204_NO_CONTENT
            return response
        return ParticipantResponse(
            id=str(participant.id),
            did=participant.did,
            protocol_url=participant.protocol_url,
            location_id=str(participant.location_id) if participant.location_id else None,
            created_at=participant.created_at.isoformat() if participant.created_at else None,
            updated_at=participant.updated_at.isoformat() if participant.updated_at else None,
        )

    async def update_participant(
        self, token: str, participant_id: str, participant: ParticipantUpdateRequest
    ) -> SimpleMessageResponse:
        # TODO all the logic for this function
        return SimpleMessageResponse(message="Participant has been updated")

    async def get_participants_count(self, token):
        # TODO auth
        return await async_postgres_service.get_participant_count()

    async def get_all_participants(self, token: str, response: Response) -> List[ParticipantResponse]:
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

        participants = await async_postgres_service.list_participants(0, None)
        for i, participant in enumerate(participants):
            participants[i] = participant.__info_to_json__()
        if not participants:
            response.status_code = status.HTTP_204_NO_CONTENT
            return []
        return participants

    async def delete_participant(self, token: str, participant_id: str = None, participant_did: str = None) -> None:
        # TODO check if auth is ok
        try:
            keycloak_service.decode_jwt_payload(token)
            if not (
                keycloak_service.token_has_realm_role(token, "admin")
                or keycloak_service.authorized_for_participant(token, participant_id)
            ):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        except HTTPException:
            raise
        except Exception:
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
