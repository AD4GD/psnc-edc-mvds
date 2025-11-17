import json

from fastapi.responses import JSONResponse
from api.core.logging_config import setup_logging
from api.models.db.registration_request import RegistrationStatus
from api.models.dto.responses import SimpleMessageResponse
from api.services.clients import async_postgres_service
from fastapi import status, Response
from . import participant_service

logger = setup_logging()


class RegistrationService:
    """ 
    Service for interacting with Registration requests related operations.
    Available only for administrators of Data Space HUB.
    """

    def __init__(self):
        pass

    async def get_all_regitrations_requests(self, token : str, response : Response):
        """ Retrieve all registration requests """
        registrations = await async_postgres_service.list_registration_requests(0, None)
        
        if not len(registrations):
            response.status_code = status.HTTP_204_NO_CONTENT
            return []
        return registrations
    
    async def get_registration_request(self, token : str, response : Response, reg_id : str):
        """ Retrieve specific registration request """
        registration_request = await async_postgres_service.get_registration_request(reg_id)
        if not registration_request:
            response.status_code = status.HTTP_204_NO_CONTENT
            return response
        return registration_request

    async def get_registration_request_count(self, token : str):
        """ Retrieve specific registration request """
        # TODO auth
        return await async_postgres_service.get_registration_request_count()
    
    async def update_registration_status(self, token : str, reg_id : str, new_status : RegistrationStatus) -> int:
        """ 
        Updates registration status with checking if can change it
        REQUESTED -> APPROVED / REJECTED
        APPROVED -> ONBOARDED
        """
        # TODO auth
        logger.info(reg_id)
        rr = await async_postgres_service.get_registration_request(reg_id)
        logger.info(rr.__info_to_json__())
        if rr is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        if \
        rr.status == RegistrationStatus.REQUESTED and new_status in [RegistrationStatus.APPROVED, RegistrationStatus.REJECTED] \
        or rr.status == RegistrationStatus.APPROVED and new_status in [RegistrationStatus.ONBOARDED, RegistrationStatus.REJECTED]:
            await async_postgres_service.update_registration_request(reg_id, {"status": new_status})
            if new_status == RegistrationStatus.APPROVED:
                # TODO actual logic to check if all participant's services for connection are working
                # TODO if services not working then <error_detail> and stay on APPROVED (availability to change it manually from admin dash)
                _ = await async_postgres_service.update_registration_request(reg_id, {"status": RegistrationStatus.ONBOARDED})
                participant = await participant_service.register_participant(reg_id=reg_id)
                if participant is None:
                    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={})  # TODO pottentially add content

                return SimpleMessageResponse(message="Participant onboarded")
            return SimpleMessageResponse(message="Status of registration has been changed")
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={ "message" : "Unsupported action" })

    async def delete_registration_request(self, token : str, reg_id : str) -> int:
        """ 
        Deletes registration request
        Function is called only when participant is being deleted
        """
        # TODO auth
        return SimpleMessageResponse(message="Record deleted") if await async_postgres_service.delete_registration_request(reg_id) > 0 else Response(status_code=status.HTTP_204_NO_CONTENT)


registration_service = RegistrationService()
