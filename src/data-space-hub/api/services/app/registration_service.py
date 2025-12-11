from api.core.logging_config import setup_logging
from api.exceptions.registration_service_exceptions import RecordNotFoundException
from api.models.db.registration_request import RegistrationStatus
from api.models.dto.responses import SimpleMessageResponse
from api.services.clients import async_postgres_service
from fastapi import Response, status
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
    async def update_registration_status(cls, token: str, reg_id: str, new_status: str) -> int:
        """
        Updates registration status with checking if can change it
        REQUESTED -> APPROVED / REJECTED
        APPROVED -> ONBOARDED
        """
        # TODO auth
        print(new_status)
        if not RegistrationStatus.__includes__(new_status):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Unsupported action"})
        target_status = RegistrationStatus(RegistrationStatus.normalize(new_status))
        rr = await async_postgres_service.get_registration_request(reg_id)

        if rr is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        if RegistrationStatus.can_transition(rr.status, target_status):
            logger.info(f"Updating registration {reg_id} to status {target_status}")
            await async_postgres_service.update_registration_request(reg_id, {"status": target_status})
            if target_status == RegistrationStatus.APPROVED:
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
