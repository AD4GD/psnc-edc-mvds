from api.core.logging_config import setup_logging
from api.services.app import vc_saver_service
from api.models.dto.requests import InsertVcRequest
from api.core.settings import FederatedCatalogSettings

logger = setup_logging()

class FederatedCatalogService:

    def __init__(self):
        self.client = None

    async def request_and_insert_vc_set(self):
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

    def health(self) -> bool:
        return True

# Singleton instance
federated_catalog_service = FederatedCatalogService()
