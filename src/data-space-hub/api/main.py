from api.core.logging import logger
from api.core.settings import ProjectSettings
from contextlib import asynccontextmanager
from api.middleware.error_handlers import register_exception_handlers
from api.routers.routers import main_router
from api.services.clients.vault_init import initialize_vault
from api.services.clients import vault_service
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Initializing Vault...")
    try:
        summary = initialize_vault(create_default_keys=True)
        logger.info(f"Vault initialized: {summary}")
    except Exception as e:
        logger.error(f"Vault initialization failed: {e}")
        # Decide if you want to fail fast or continue
        raise
    
    # Check health
    if vault_service.health():
        logger.info("✅ Vault is healthy and ready")
    else:
        logger.warning("⚠️  Vault health check failed")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title=ProjectSettings.service_name,
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None,
    description="Registration Service for Data Space",
    version=ProjectSettings.service_version,
    lifespan=lifespan
)
logger.instrument_fastapi(app)

register_exception_handlers(app)

app.include_router(main_router)
