from api.core.logging import logger
from api.core.settings import ProjectSettings
from api.exceptions.registration_service_exceptions import ServiceUnavailableException
from api.models.dto.error_responses import ErrorResponse
from api.models.dto.responses import HealthResponse
from api.services.clients.postgres_service import async_postgres_service
from api.services.clients.keycloak_service import keycloak_service
from api.services.clients.vault_service import vault_service
from fastapi import APIRouter, status

health_router = APIRouter()


@health_router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def health_check():
    try:
        async_postgres_health = await async_postgres_service.health()
        sync_keycloak_health = keycloak_service.health()
        sync_vault_health = vault_service.health()
        if all([async_postgres_health, sync_keycloak_health, sync_vault_health]):
            status = "UP"
        else:
            status = "DOWN"
        return HealthResponse(
            status=status,
            service=ProjectSettings.service_name,
            version=ProjectSettings.service_version,
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise ServiceUnavailableException()
