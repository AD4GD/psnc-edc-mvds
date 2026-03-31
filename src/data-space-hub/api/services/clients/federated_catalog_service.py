from api.core.logging_config import setup_logging
from api.core.settings import FederatedCatalogSettings
import httpx
from fastapi import FastAPI, HTTPException
import base64

logger = setup_logging()

class FederatedCatalogService:

    def __init__(self):
        self.client = None

    async def create_target_node(self, did, dsp_url):
        """Add a participant as a target node in the Federated Catalog."""
        url = f"{FederatedCatalogSettings.targets_url}/v1/targets"
        headers = {"x-api-key": FederatedCatalogSettings.api_key, "Content-Type": "application/json"}
        body = {
            "participantId": did,
            "url": dsp_url,
            "supportedProtocols": ["dataspace-protocol-http"]
        }

        async with httpx.AsyncClient(timeout=10) as client:
          r = await client.post(url, headers=headers, json=body)
          if r.status_code not in (200, 201, 204):
              raise HTTPException(status_code=502, detail={"create_target_node_error": r.text})
          return r.json() if r.text else {}

    async def remove_target_node(self, did):
        """Remove a participant target node from the Federated Catalog."""
        participant_context_id_base64 = self._encode_participant_context_id(did)

        url = f"{FederatedCatalogSettings.targets_url}/v1/targets/{participant_context_id_base64}"
        headers = {"x-api-key": FederatedCatalogSettings.api_key, "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=10) as client:
          r = await client.delete(url, headers=headers)
          if r.status_code not in (200, 201, 204):
              raise HTTPException(status_code=502, detail={"remove_target_node_error": r.text})
          return r.json() if r.text else {}

    def health(self) -> bool:
        return True
    
    def _encode_participant_context_id(self, participant_id: str) -> str:
      # Base64-encode the exact participantId string used at creation time
      return base64.b64encode(participant_id.encode("utf-8")).decode("ascii")

# Singleton instance
federated_catalog_service = FederatedCatalogService()
