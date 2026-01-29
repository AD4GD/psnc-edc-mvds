from contextlib import asynccontextmanager

from api.core.logging_config import setup_logging
from api.core.settings import ProjectSettings
from api.middleware.error_handlers import register_exception_handlers
from api.routers.routers import main_router, public_router
from api.services.clients import vault_service, federated_catalog_service
from api.services.clients.vault_init import initialize_vault
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Initializing Vault...")
    try:
        logger.info("Waiting for dependent services to initialize...")
        await asyncio.sleep(20)
        summary = initialize_vault(create_default_keys=True)
        logger.info(f"Vault initialized: {summary}")
    except Exception as e:
        logger.error(f"Vault initialization failed: {e}")
        # Decide if you want to fail fast or continue
        raise

    logger.info("Requesting VCs set...")
    try:
        logger.info("Waiting for dependent services to initialize...")
        await asyncio.sleep(15)

        summary = await federated_catalog_service.request_and_save_vc_set()
        logger.info(f"VCs has been saved: {summary}")
    except Exception as e:
        logger.error(f"VCs set initialization failed: {e}")
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
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)

register_exception_handlers(app)

app.include_router(main_router)
app.include_router(public_router)