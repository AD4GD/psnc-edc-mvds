from api.core.logging_config import setup_logging
from api.models.db.registration_request import RegistrationStatus
from api.models.dto.responses import SimpleMessageResponse
from api.services.clients import async_postgres_service
from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from api.exceptions.registration_service_exceptions import RecordNotFoundException
from api.models.db.registration_request import RegistrationRequest, RegistrationStatus
from api.models.dto.requests import UserCreateRequest
from api.models.dto.responses import ParticipantResponse, SimpleMessageResponse
from api.services.clients import EmailService, async_postgres_service, keycloak_service
from uuid import uuid4

from api.core.logging_config import setup_logging
from api.services.infrastructure import RegistrationTokenService, registration_token_service
from api.services.helper import create_did
from api.templates.email import participant_accepted_template, participant_confirm_email_template
from api.templates.template_filler import render_jinja_template

from . import participant_service

logger = setup_logging()


class RegistrationService:
    """
    Service for interacting with Registration requests related operations.
    Available only for administrators of Data Space HUB.
    """

    def __init__(self):
        pass

    @classmethod
    async def start_participant_registration(cls, request: UserCreateRequest) -> SimpleMessageResponse:
        """
        Start participant registration process.
        Participant sends a request with a form, it is then saved to db into registration_request and email is sent.
        """
        request_id = uuid4()
        payload = {
            "id": request_id,
            "status": RegistrationStatus.REQUESTED.value,
            "request_form": jsonable_encoder(request),
            "error_detail": None,
            "email_confirmed": False,
        }
        response = await async_postgres_service.create_registration_request(payload)
        logger.info(f"Created new registration - {response.id}")
        
        email_confirmation_link = await cls._get_email_confirmation_url(request_id)
        logger.info(email_confirmation_link)

        email_response = EmailService.send_email(
            recipients=[request.email],
            subject="Confirm your email",
            body=render_jinja_template(
                participant_confirm_email_template,
                {
                    "participant_name": request.name, 
                    "confirmation_link": email_confirmation_link
                },
            ),
            body_type="html",
        )
        logger.info(email_response)

        return SimpleMessageResponse(message="OK")
    
    @classmethod
    async def _get_email_confirmation_url(cls, request_id):
        token = await registration_token_service.generate_token(request_id)
        return f"http://localhost:8300/api/v1/registration/requests/{request_id}/email-confirm?token={token}"

    @classmethod
    async def assert_registration_token(cls, request_id, token):
        is_valid = await registration_token_service.is_valid_token(request_id, token)
        if is_valid:
            await registration_token_service.consume_token(request_id, token)
            
        return is_valid
    
    @classmethod
    async def confirm_email(cls, request_id):
        await async_postgres_service.confirm_email(request_id)

    @classmethod
    async def register_participant(cls, reg_id) -> ParticipantResponse:
        """Register a new participant with the provided information."""
        # TODO check content of request
        reg_req: RegistrationRequest = await async_postgres_service.get_registration_request(reg_id)
        form: UserCreateRequest = reg_req.request_form

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

    @classmethod
    async def get_all_regitrations_requests(cls, offset: int = 0, limit: int | None = None):
        """Retrieve all registration requests"""
        registrations = await async_postgres_service.list_registration_requests(offset, limit)
        return registrations

    @classmethod
    async def get_registration_request(cls, reg_id: str):
        """Retrieve specific registration request"""
        registration_request = await async_postgres_service.get_registration_request(reg_id)
        return registration_request

    @classmethod
    async def get_registration_requests_count(cls):
        return await async_postgres_service.get_registration_requests_count()

    @classmethod
    async def update_registration_status(cls, reg_id: str, new_status: RegistrationStatus) -> int:
        """
        Updates registration status with checking if can change it
        REQUESTED -> APPROVED / REJECTED
        APPROVED -> ONBOARDED
        """
        logger.info(reg_id)
        rr = await async_postgres_service.get_registration_request(reg_id)
        if rr is None:
            raise RecordNotFoundException()

        logger.info(rr.__info_to_json__())
        if (
            rr.status == RegistrationStatus.REQUESTED
            and new_status in [RegistrationStatus.APPROVED, RegistrationStatus.REJECTED]
            or rr.status == RegistrationStatus.APPROVED
            and new_status in [RegistrationStatus.ONBOARDED, RegistrationStatus.REJECTED]
        ):
            await async_postgres_service.update_registration_request(reg_id, {"status": new_status})
            if new_status == RegistrationStatus.APPROVED:
                # TODO actual logic to check if all participant's services for connection are working
                # TODO if services not working then <error_detail> and stay on APPROVED (availability to change it manually from admin dash)
                _ = await async_postgres_service.update_registration_request(reg_id, {"status": RegistrationStatus.ONBOARDED})
                #participant = await participant_service.register_participant(reg_id=reg_id)
                #if participant is None:
                #    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={})  # TODO pottentially add content

                return SimpleMessageResponse(message="Participant onboarded")
            return SimpleMessageResponse(message="Status of registration has been changed")
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Unsupported action"})

    @classmethod
    async def delete_registration_request(cls, reg_id: str) -> int:
        """
        Deletes registration request
        Function is called only when participant is being deleted
        """
        return (
            SimpleMessageResponse(message="Record deleted")
            if await async_postgres_service.delete_registration_request(reg_id) > 0
            else Response(status_code=status.HTTP_204_NO_CONTENT)
        )


registration_service = RegistrationService()
