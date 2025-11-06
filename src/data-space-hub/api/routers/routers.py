from api.routers.health import health_router
from api.routers.participant import router as participant_router
from api.routers.user import router as user_router
from api.routers.registration import router as registration_router
from fastapi import APIRouter

main_router = APIRouter(prefix="/api/v3")

main_router.include_router(health_router, tags=["Health"])
main_router.include_router(participant_router, tags=["Participant", "Manage", "Register", "Delete"])
main_router.include_router(user_router, tags=["User", "Register"])
main_router.include_router(registration_router, tags=["Participant", "Register"])
