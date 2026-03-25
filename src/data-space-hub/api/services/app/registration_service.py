from uuid import uuid4

from api.core.logging_config import setup_logging
from api.core.settings import ProjectSettings
from api.exceptions.registration_service_exceptions import RecordNotFoundException
from api.models.db.registration_request import RegistrationStatus
from api.models.dto.requests import ParticipantCreateRequest, InsertVcRequest
from api.models.dto.responses import SimpleMessageResponse
from api.services.clients import EmailService, async_postgres_service
from api.services.infrastructure import registration_token_service
from api.templates.email import participant_confirm_email_template
from api.templates.template_filler import render_jinja_template
from fastapi import Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

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
    async def start_participant_registration(cls, request: ParticipantCreateRequest) -> SimpleMessageResponse:
        """
        Start participant registration process.
        Participant sends a request with a form, it is then saved to db into registration_request and email is sent.
        """
        payload = {
            "id": uuid4(),
            "status": RegistrationStatus.REQUESTED.value,
            "request_form": jsonable_encoder(request),
            "error_detail": "",  # Test for some error details
            "email_confirmed": False,
        }
        rr = await async_postgres_service.create_registration_request(payload)
        logger.info(f"Created new registration - {rr.id}")

        email_confirmation_link = await cls._get_email_confirmation_url(rr.id)
        logger.info(email_confirmation_link)

        email_response = EmailService.send_email(
            recipients=[request.email],
            subject="Confirm your email",
            body=render_jinja_template(
                participant_confirm_email_template,
                {"participant_name": request.full_name, "confirmation_link": email_confirmation_link},
            ),
            body_type="html",
        )
        logger.info(email_response)
        # TODO after participant admin email confirmation - send email to DS admin
        return SimpleMessageResponse(message="Everything OK")  # Make correct response

    @classmethod
    async def _get_email_confirmation_url(cls, request_id):
        token = await registration_token_service.generate_token(request_id)
        return f"{ProjectSettings.app_url}/api/v1/registration/request/{request_id}/email-confirm?token={token}"

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
    async def get_all_regitrations_requests(cls, token: str, response: Response, offset: int = 0, limit: int | None = None):
        """Retrieve all registration requests"""
        registrations = await async_postgres_service.list_registration_requests(offset, limit)

        if not registrations:
            raise RecordNotFoundException(message="No registration requests found", status_code=204, record_type="registration request list")
        return registrations

    @classmethod
    async def get_registration_request(cls, token: str, response: Response, reg_id: str):
        """Retrieve specific registration request"""
        registration_request = await async_postgres_service.get_registration_request(reg_id)
        if not registration_request:
            raise RecordNotFoundException(
                message="Registration request not found", status_code=204, record_id=reg_id, record_type="registration request"
            )
        return registration_request

    @classmethod
    async def get_registration_request_count(cls, token: str):
        """Retrieve specific registration request"""
        # TODO auth
        return await async_postgres_service.get_registration_request_count()

    @classmethod
    async def update_registration_status(cls, reg_id: str, new_status: str) -> int:
        """
        Updates registration status with checking if can change it
        REQUESTED -> APPROVED / REJECTED
        APPROVED -> ONBOARDED
        """
        logger.info(new_status)

        # TODO auth
        if not RegistrationStatus.__includes__(new_status):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Unsupported action"})
        target_status = RegistrationStatus.normalize(new_status)
        rr = await async_postgres_service.get_registration_request(reg_id)

        logger.info(rr)

        if rr is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        if not rr.email_confirmed:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Email not confirmed yet"})
        
        if RegistrationStatus.can_transition(rr.status, target_status):
            logger.info(f"Updating registration {reg_id} to status {target_status}")
            await async_postgres_service.update_registration_request(reg_id, {"status": target_status})
            if new_status == RegistrationStatus.APPROVED:

                await cls._issue_vc_and_add_to_federated_catalog(rr.request_form['data_space_components'])

                # TODO actual logic to check if all participant's services for connection are working
                # TODO if services not working then <error_detail> and stay on APPROVED (availability to change it manually from admin dash)
                logger.info(f"Updating registration {reg_id} to status {RegistrationStatus.ONBOARDED.value}")
                _ = await async_postgres_service.update_registration_request(reg_id, {"status": RegistrationStatus.ONBOARDED.value})
                participant = await participant_service.register_participant(reg_id=reg_id)
                if participant is None:
                    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={})  # TODO pottentially add content
            
                return SimpleMessageResponse(message="Participant onboarded")
            return SimpleMessageResponse(message=f"Status of registration has been changed to {target_status}")
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Unsupported action"})

    @classmethod
    async def _issue_vc_and_add_to_federated_catalog(cls, request_form) -> int:
        
        insert_vc_request = InsertVcRequest(**request_form)

        from api.services.app.vc_saver_service import vc_saver_service
        from api.services.clients.federated_catalog_service import federated_catalog_service

        await vc_saver_service.issue_and_store_vcs(insert_vc_request)
        await federated_catalog_service.create_target_node(insert_vc_request.connector_did, insert_vc_request.connector_dsp_url)

    @classmethod
    async def delete_registration_request(cls, token: str, reg_id: str) -> int:
        """
        Deletes registration request
        Function is called only when participant is being deleted
        """
        # TODO auth
        return (
            SimpleMessageResponse(message="Record deleted")
            if await async_postgres_service.delete_registration_request(reg_id) > 0
            else Response(status_code=status.HTTP_204_NO_CONTENT)
        )


registration_service = RegistrationService()
