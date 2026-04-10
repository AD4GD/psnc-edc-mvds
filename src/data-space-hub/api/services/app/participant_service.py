from typing import List
from uuid import uuid4

from api.core.logging_config import setup_logging
from api.exceptions.registration_service_exceptions import RecordNotFoundException, UnauthorizedException
from api.models.db.registration_request import RegistrationRequest
from api.models.dto.requests import ParticipantCreateRequest, ParticipantUpdateRequest
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse
from api.services.clients import EmailService, async_postgres_service, keycloak_service
from api.templates.email import participant_offboarded_template
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
                    "data_space_components": form.get("data_space_components", {}),
                    "location_id": location.id,
                    "VAT_number": form["VAT_number"],
                    "email": form["email"],
                },
                session=session,
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
    async def delete_participant(cls, token: str, participant_id: str, reason: str = "") -> SimpleMessageResponse:
        """
        Full offboarding of a participant (admin-initiated).
        Steps:
          1. Auth: must be admin
          2. Load participant from DB to get their email and name
          3. Delete Keycloak user (soft-fail: log warning if not found)
          4. Delete participant DB record (cascades location via separate call)
          5. Mark registration request as REJECTED (audit trail)
          6. Send offboarding notification email to the participant
        """
        try:
            keycloak_service.require_admin(token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

        participant = await async_postgres_service.get_participant(participant_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

        participant_email = participant.email
        participant_name = participant.full_name or participant.name

        # 1. Remove from Keycloak (best-effort)
        try:
            keycloak_service.delete_user_by_email(participant_email)
        except Exception as kc_err:
            logger.warning(f"Could not delete Keycloak user for {participant_email}: {kc_err}")

        # 2. Delete participant record (DB)
        deleted = await async_postgres_service.delete_participant(p_id=participant_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete participant record")

        # 3. Mark registration as REJECTED for audit trail
        try:
            rr = await async_postgres_service.get_registration_request_by_participant_id(participant_id)
            if rr:
                from api.models.db.registration_request import RegistrationStatus
                await async_postgres_service.update_registration_request(
                    rr.id,
                    {
                        "status": RegistrationStatus.REJECTED.value,
                        "error_detail": f"Offboarded by admin. Reason: {reason}" if reason else "Offboarded by admin.",
                    },
                )
        except Exception as rr_err:
            logger.warning(f"Could not update registration request during offboarding: {rr_err}")

        # 4. Send offboarding email
        try:
            EmailService.send_email(
                recipients=[participant_email],
                subject="Data Space – Your organization has been offboarded",
                body=render_jinja_template(
                    participant_offboarded_template,
                    {
                        "participant_name": participant_name,
                        "initiated_by": "admin",
                        "reason": reason,
                    },
                ),
                body_type="html",
            )
        except Exception as mail_err:
            logger.warning(f"Offboarding email failed for {participant_email}: {mail_err}")

        logger.info(f"Participant {participant_id} ({participant_email}) offboarded by admin")
        return SimpleMessageResponse(message=f"Participant '{participant_name}' has been offboarded")

    @classmethod
    async def offboard_self(cls, token: str, reason: str = "") -> SimpleMessageResponse:
        """
        Self-offboarding: the authenticated participant removes their own organization.
        Steps:
          1. Resolve participant_id from token
          2. Confirm the caller is the owner of that participant
          3. Delegate to delete_participant logic (minus the admin check)
        """
        participant_id = keycloak_service.get_participant_id_from_token(token)
        if not participant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No participant linked to your account")

        participant = await async_postgres_service.get_participant(participant_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

        participant_email = participant.email
        participant_name = participant.full_name or participant.name

        # Verify the token email matches the participant email (ownership check)
        token_payload = keycloak_service.decode_jwt_payload(token)
        token_email = token_payload.get("email", "")
        if token_email and token_email.lower() != participant_email.lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token does not match participant email")

        # 1. Delete Keycloak user (best-effort)
        try:
            keycloak_service.delete_user_by_email(participant_email)
        except Exception as kc_err:
            logger.warning(f"Could not delete Keycloak user for {participant_email}: {kc_err}")

        # 2. Delete participant record
        deleted = await async_postgres_service.delete_participant(p_id=str(participant_id))
        if not deleted:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete participant record")

        # 3. Mark registration as REJECTED for audit trail
        try:
            rr = await async_postgres_service.get_registration_request_by_participant_id(str(participant_id))
            if rr:
                from api.models.db.registration_request import RegistrationStatus
                await async_postgres_service.update_registration_request(
                    rr.id,
                    {
                        "status": RegistrationStatus.REJECTED.value,
                        "error_detail": f"Self-offboarded. Reason: {reason}" if reason else "Self-offboarded by participant.",
                    },
                )
        except Exception as rr_err:
            logger.warning(f"Could not update registration request during self-offboarding: {rr_err}")

        # 4. Send offboarding email
        try:
            EmailService.send_email(
                recipients=[participant_email],
                subject="Data Space – Offboarding confirmed",
                body=render_jinja_template(
                    participant_offboarded_template,
                    {
                        "participant_name": participant_name,
                        "initiated_by": "self",
                        "reason": reason,
                    },
                ),
                body_type="html",
            )
        except Exception as mail_err:
            logger.warning(f"Offboarding email failed for {participant_email}: {mail_err}")

        logger.info(f"Participant {participant_id} ({participant_email}) self-offboarded")
        return SimpleMessageResponse(message="Your organization has been offboarded from the Data Space")


participant_service = ParticipantService()
