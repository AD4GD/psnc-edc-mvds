from api.routers.health import health_router
from api.routers.participant import router as participant_router
from api.routers.registration import router as registration_router
from api.routers.vc import router as vc_router
from fastapi import APIRouter

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(health_router, tags=["Health"])
main_router.include_router(participant_router, tags=["Participant"])
main_router.include_router(registration_router, tags=["Registration"])
main_router.include_router(vc_router, tags=["Verifiable Credentials"])
