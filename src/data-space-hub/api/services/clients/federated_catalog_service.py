from api.core.logging_config import setup_logging
from api.services.app import vc_saver_service
from api.models.dto.requests import InsertVcRequest
from api.core.settings import FederatedCatalogSettings
import httpx
from fastapi import FastAPI, HTTPException
import base64

logger = setup_logging()

class FederatedCatalogService:

    def __init__(self):
        self.client = None

    async def request_and_save_vc_set(self):
        body = InsertVcRequest(
            connector_did=FederatedCatalogSettings.did,
            connector_dsp_url=FederatedCatalogSettings.dsp_url,
            connector_management_url=FederatedCatalogSettings.management_url,
            connector_api_key=FederatedCatalogSettings.api_key,
            identity_hub_identity_url=FederatedCatalogSettings.identity_hub_identity_url,
            identity_hub_credentials_url=FederatedCatalogSettings.identity_hub_credentials_url,
            identity_hub_api_key=FederatedCatalogSettings.identity_hub_api_key,
            sts_public_key_pem=FederatedCatalogSettings.sts_public_key_pem,
            generated_vcs=[]
        )
        await vc_saver_service.create_participant_and_save_vc(body)
        return {
            "status": "OK"
        }
    
    async def create_target_node(self, did, dsp_url):
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
              raise HTTPException(status_code=502, detail={"create_participant_error": r.text})
          return r.json() if r.text else {}

    async def remove_target_node(self, did):
        participant_context_id_base64 = self._encode_participant_context_id(did)

        url = f"{FederatedCatalogSettings.targets_url}/v1/targets/{participant_context_id_base64}"
        headers = {"x-api-key": FederatedCatalogSettings.api_key, "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=10) as client:
          r = await client.delete(url, headers=headers)
          if r.status_code not in (200, 201, 204):
              raise HTTPException(status_code=502, detail={"create_participant_error": r.text})
          return r.json() if r.text else {}

    def health(self) -> bool:
        return True
    
    def _encode_participant_context_id(self, participant_id: str) -> str:
      # Base64-encode the exact participantId string used at creation time
      return base64.b64encode(participant_id.encode("utf-8")).decode("ascii")

# Singleton instance
federated_catalog_service = FederatedCatalogService()
