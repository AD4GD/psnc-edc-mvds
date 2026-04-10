from api.core.logging_config import setup_logging
from api.services.clients import async_postgres_service, keycloak_service
from api.services.helper import get_bearer_token
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

logger = setup_logging()
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current user info from Keycloak token",
)
async def get_me(token: str = Depends(get_bearer_token)):
    """
    Returns current user information extracted from the Keycloak token.
    Includes user profile, roles, and linked participant (if any).
    """
    try:
        # Validate token
        introspection = keycloak_service.introspect_token(token)
        if not introspection.get("active"):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": "Token is inactive"})

        payload = keycloak_service.decode_jwt_payload(token)

        # Extract basic user info
        user_id = payload.get("sub")
        email = payload.get("email", "")
        name = payload.get("name", "")
        preferred_username = payload.get("preferred_username", "")
        realm_roles = payload.get("realm_access", {}).get("roles", [])

        is_admin = "admin" in realm_roles or "rs-admin" in realm_roles

        # Try to find linked participant
        participant_id = payload.get("participant_id")
        participant = None

        if participant_id:
            try:
                p = await async_postgres_service.get_participant(participant_id)
                if p:
                    participant = p.to_dict()
            except Exception:
                logger.warning(f"Could not load participant {participant_id} for user {user_id}")

        return {
            "user_id": user_id,
            "email": email,
            "name": name,
            "preferred_username": preferred_username,
            "is_admin": is_admin,
            "roles": realm_roles,
            "participant_id": participant_id,
            "participant": participant,
        }

    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error in /auth/me: {e}")
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": "Authentication failed"})
