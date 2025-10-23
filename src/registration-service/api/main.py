from api.core.logging import logger
from api.core.settings import ProjectSettings
from api.middleware.error_handlers import register_exception_handlers
from api.routers.routers import main_router
from fastapi import FastAPI

app = FastAPI(
    title=ProjectSettings.service_name,
    description="Registration Service for Data Space",
    version=ProjectSettings.service_version,
)
logger.instrument_fastapi(app)

register_exception_handlers(app)

app.include_router(main_router)
