from api.core.logging_config import setup_logging
from api.core.settings import FederatedCatalogSettings
from api.services.helper import require_admin_token
from fastapi import APIRouter, Depends, HTTPException
import httpx

logger = setup_logging()
router = APIRouter(prefix="/fc", tags=["Federated Catalog"])


@router.get(
    "/targets",
    summary="List all target nodes registered in the Federated Catalog (admin)",
)
async def list_fc_targets(token: str = Depends(require_admin_token)):
    """
    Proxy GET /v1/targets from the Federated Catalog and return the list of
    registered target nodes. Used by the admin portal to display FC status
    per participant.
    """
    url = f"{FederatedCatalogSettings.targets_url}/v1/targets"
    headers = {
        "x-api-key": FederatedCatalogSettings.api_key,
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=headers)
        if r.status_code == 204 or not r.text:
            return []
        if r.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail=f"FC returned {r.status_code}: {r.text}")
        return r.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Federated Catalog: {exc}")
