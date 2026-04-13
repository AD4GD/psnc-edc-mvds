from __future__ import annotations

from typing import Annotated

from api.core.logging_config import setup_logging
from api.models.dto.responses import SimpleMessageResponse, VCResponse
from api.services.app import vc_saver_service
from api.services.helper import require_dsh_api_key, get_bearer_token
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from api.models.dto.requests import InsertVcRequest
from api.services.clients import federated_catalog_service, keycloak_service, async_postgres_service

logger = setup_logging()
router = APIRouter(prefix="/verifiable-credentials", tags=["Verifiable Credentials"])


@router.get(
    "",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Allow participant to generate new VCs for its users when keys rotate",
)
def test_endpoint():
    """
    Test endpoint with various stages
    """
    return SimpleMessageResponse(message="Test endpoint reached successfully")

@router.post(
    "/issue",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Issue VCs for a participant and register in federated catalog",
    dependencies=[Depends(require_dsh_api_key)],
)
async def issue_vc(body: Annotated[InsertVcRequest, Body()]):
    """
    Issue Verifiable Credentials for a participant and add them as a target
    node in the Federated Catalog. Identity Hub participant context creation
    and STS secret storage are handled externally by the init-dataspace script.

    Requires a valid x-api-key header.
    """
    await vc_saver_service.issue_and_store_vcs(body)
    await federated_catalog_service.create_target_node(body.connector_did, body.connector_dsp_url)
    return None


@router.post(
    "/request",
    status_code=status.HTTP_200_OK,
    summary="Request VC issuance for an authenticated participant",
)
async def request_vc(body: Annotated[InsertVcRequest, Body()], token: str = Depends(get_bearer_token)):
    """
    Authenticated participant requests VC issuance for their connector.
    The participant must be logged in (Keycloak bearer token).
    This issues VCs and registers the connector in the federated catalog.
    """
    try:
        # Validate the token
        keycloak_service.introspect_token(token)
    except Exception:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": "Invalid or expired token"})

    # Get participant via Keycloak 'sub' stored in keycloak_id column
    keycloak_id = keycloak_service.get_keycloak_id_from_token(token)
    if not keycloak_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "No participant linked to this account. Contact admin."},
        )

    # Verify participant exists
    participant = await async_postgres_service.get_participant_by_keycloak_id(keycloak_id)
    if not participant:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Participant not found"},
        )

    try:
        await vc_saver_service.issue_and_store_vcs(body)
        await federated_catalog_service.create_target_node(body.connector_did, body.connector_dsp_url)

        # Update participant's data_space_components with the latest connector info
        await async_postgres_service.update_participant(
            participant.id,
            {
                "data_space_components": {
                    "connector_did": body.connector_did,
                    "connector_dsp_url": body.connector_dsp_url,
                    "identity_hub_identity_url": body.identity_hub_identity_url,
                    "identity_hub_api_key": body.identity_hub_api_key,
                }
            },
        )

        return SimpleMessageResponse(message="VCs issued and connector registered successfully")
    except Exception as e:
        logger.error(f"VC request failed for participant {participant.id}: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"VC issuance failed: {str(e)}"},
        )