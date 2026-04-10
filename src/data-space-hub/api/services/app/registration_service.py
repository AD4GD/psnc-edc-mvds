from uuid import uuid4

from api.core.logging_config import setup_logging
from api.core.settings import ProjectSettings
from api.exceptions.registration_service_exceptions import RecordNotFoundException
from api.models.db.registration_request import RegistrationStatus
from api.models.dto.requests import RegistrationCreateRequest, InsertVcRequest
from api.models.dto.responses import SimpleMessageResponse
from api.services.clients import EmailService, async_postgres_service, keycloak_service
from api.services.infrastructure import registration_token_service
from api.templates.email import (
    participant_confirm_email_template,
    participant_accepted_template,
    participant_rejected_template,
    participant_set_password_template,
    admin_waiting_for_appoval_template,
)
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
    async def start_participant_registration(cls, request: RegistrationCreateRequest) -> SimpleMessageResponse:
        """
        Start participant registration process.
        Participant sends a request with company info only, it is saved to db and confirmation email is sent.
        """
        payload = {
            "id": uuid4(),
            "status": RegistrationStatus.REQUESTED.value,
            "request_form": jsonable_encoder(request),
            "error_detail": "",
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
        return SimpleMessageResponse(message="Registration submitted. Please check your email to confirm.")

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

        # Notify DS admin that a new registration is waiting for review
        rr = await async_postgres_service.get_registration_request(request_id)
        if rr and rr.request_form:
            form = rr.request_form
            try:
                # Send notification to admin email (use the configured admin email or a dedicated one)
                admin_email = getattr(ProjectSettings, "admin_email", None)
                if admin_email:
                    EmailService.send_email(
                        recipients=[admin_email],
                        subject="New participant registration awaiting approval",
                        body=render_jinja_template(
                            admin_waiting_for_appoval_template,
                            {
                                "participant_name": form.get("full_name", form.get("name", "Unknown")),
                                "participant_email": form.get("email", "Unknown"),
                            },
                        ),
                        body_type="html",
                    )
                    logger.info(f"Admin notification sent for registration {request_id}")
                else:
                    logger.warning("No admin_email configured – skipping admin notification")
            except Exception as e:
                logger.error(f"Failed to send admin notification for registration {request_id}: {e}")

    @classmethod
    async def get_all_regitrations_requests(cls, token: str, response: Response, offset: int = 0, limit: int | None = None):
        """Retrieve all registration requests"""
        registrations = await async_postgres_service.list_registration_requests(offset, limit)

        if not registrations:
            return []
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
        return await async_postgres_service.get_registration_request_count()

    @classmethod
    async def update_registration_status(cls, reg_id: str, new_status: str, reject_reason: str = "") -> int:
        """
        Updates registration status with checking if can change it
        REQUESTED -> APPROVED / REJECTED
        APPROVED -> ONBOARDED
        """
        logger.info(new_status)

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
                form = rr.request_form
                kc_user_id = None

                # 1. Create Keycloak user so the participant can log in to the portal
                try:
                    # This is a company/organisation account – use the short name as
                    # firstName and the full legal name as lastName.  Keycloak requires
                    # both fields but they carry no personal meaning here.
                    kc_user_id = keycloak_service.create_user(
                        email=form["email"],
                        first_name=form.get("name", ""),
                        last_name=form.get("full_name", form.get("name", "")),
                        attributes={"registration_id": str(reg_id)},
                    )

                    # Assign participant role
                    try:
                        keycloak_service.assign_realm_role(kc_user_id, "participant")
                    except Exception as role_err:
                        logger.warning(f"Could not assign 'participant' role (may not exist): {role_err}")

                    # Set a temporary password and send credentials via our own email service
                    temp_password = keycloak_service.set_temporary_password(kc_user_id)
                    EmailService.send_email(
                        recipients=[form["email"]],
                        subject="Data Space - Your Account Credentials",
                        body=render_jinja_template(
                            participant_set_password_template,
                            {
                                "participant_name": form.get("full_name", form.get("name", "")),
                                "email": form["email"],
                                "temporary_password": temp_password,
                                "portal_url": ProjectSettings.frontend_url,
                            },
                        ),
                        body_type="html",
                    )
                    logger.info(f"Keycloak user created for {form['email']}, credentials email sent via email-service")
                except Exception as e:
                    logger.error(f"Failed to create Keycloak user for registration {reg_id}: {e}")
                    # Roll back status to REQUESTED so admin can retry
                    await async_postgres_service.update_registration_request(
                        reg_id, {
                            "status": RegistrationStatus.REQUESTED.value,
                            "error_detail": f"Keycloak user creation failed: {e}",
                        }
                    )
                    return JSONResponse(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"message": f"Onboarding failed at Keycloak user creation: {e}"},
                    )

                # 2. Create participant record in DB
                participant = await participant_service.register_participant(reg_id=reg_id)
                if participant is None:
                    await async_postgres_service.update_registration_request(
                        reg_id, {
                            "status": RegistrationStatus.REQUESTED.value,
                            "error_detail": "Failed to create participant record in database",
                        }
                    )
                    return JSONResponse(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"message": "Onboarding failed: could not create participant record"},
                    )

                # 3. Update Keycloak user attribute with participant_id for token mapping
                try:
                    participant_id = str(participant.id) if hasattr(participant, 'id') else str(participant.get('id', ''))
                    if kc_user_id and participant_id:
                        keycloak_service.keycloak_admin.update_user(
                            user_id=kc_user_id,
                            payload={"attributes": {"participant_id": participant_id, "registration_id": str(reg_id)}},
                        )
                except Exception as e:
                    logger.warning(f"Could not update Keycloak user attributes: {e}")

                # 4. Transition to ONBOARDED
                logger.info(f"Updating registration {reg_id} to status {RegistrationStatus.ONBOARDED.value}")
                await async_postgres_service.update_registration_request(
                    reg_id, {"status": RegistrationStatus.ONBOARDED.value, "error_detail": ""}
                )

                # 5. Send accepted email to participant
                EmailService.send_email(
                    [form["email"]],
                    "Data Space - Registration Approved",
                    render_jinja_template(participant_accepted_template, {"participant_name": form.get("full_name", form.get("name", ""))}),
                    "html",
                )

                return SimpleMessageResponse(message="Participant approved and onboarded")

            if new_status == RegistrationStatus.REJECTED:
                form = rr.request_form
                # Save rejection reason
                if reject_reason:
                    await async_postgres_service.update_registration_request(reg_id, {"error_detail": reject_reason})

                # Send rejection email
                try:
                    EmailService.send_email(
                        [form["email"]],
                        "Data Space - Registration Rejected",
                        render_jinja_template(
                            participant_rejected_template,
                            {
                                "participant_name": form.get("full_name", form.get("name", "")),
                                "reject_reason": reject_reason or "No reason provided.",
                            },
                        ),
                        "html",
                    )
                except Exception as e:
                    logger.error(f"Failed to send rejection email for {reg_id}: {e}")

            return SimpleMessageResponse(message=f"Status of registration has been changed to {target_status}")
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Unsupported action"})

    @classmethod
    async def retry_onboarding(cls, reg_id: str):
        """
        Retry the onboarding process for a registration that previously failed.
        Allowed when the registration is in REQUESTED state with a non-empty error_detail
        (i.e. it was rolled back after a failure during approval).
        Re-runs the same approval logic.
        """
        rr = await async_postgres_service.get_registration_request(reg_id)
        if rr is None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Registration not found"})

        if rr.status not in (RegistrationStatus.REQUESTED.value, RegistrationStatus.REQUESTED):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"message": f"Retry is only allowed for registrations in REQUESTED state (current: {rr.status})"},
            )

        if not rr.error_detail:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"message": "No previous error recorded – use the normal approve flow instead"},
            )

        # Clear the previous error and re-attempt approval
        await async_postgres_service.update_registration_request(reg_id, {"error_detail": ""})
        return await cls.update_registration_status(reg_id, RegistrationStatus.APPROVED)

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
        return (
            SimpleMessageResponse(message="Record deleted")
            if await async_postgres_service.delete_registration_request(reg_id) > 0
            else Response(status_code=status.HTTP_204_NO_CONTENT)
        )


registration_service = RegistrationService()
