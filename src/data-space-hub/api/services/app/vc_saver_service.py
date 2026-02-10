# from datetime import datetime, timezone
# from uuid import uuid4

# import httpx
from api.core.logging_config import setup_logging

# from api.models.db import IssuedCredentials, Participant
from api.services.clients import async_postgres_service, vault_service
import httpx
from fastapi import FastAPI, HTTPException
from api.templates.template_filler import render_jinja_template
import json
import base64
import time
from api.models.dto.requests import InsertVcRequest, GenerateVcRequest
from api.services.app.vc_generator_service import vc_generator_service

logger = setup_logging()

PARTICIPANT_DATA_TEMPLATE = """
  {
    "roles":[],
    "serviceEndpoints":[
      {
        "type": "CredentialService",
        "serviceEndpoint": "{{ credential_service_endpoint }}",
        "id": "credentialservice-1"
      },
      {
        "type": "ProtocolEndpoint",
        "serviceEndpoint": "{{ protocol_service_endpoint }}",
        "id": "dsp"
      }
    ],
    "active": true,
    "participantId": "{{ participant_did }}",
    "did": "{{ participant_did }}",
    "key":{
      "keyId": "{{ participant_did }}#key-1",
      "privateKeyAlias": "key-1",
      "publicKeyPem":"{{ pem_value }}"
    }
  }
"""

SECRETS_DATA_TEMPLATE = """
{
  "@context": {
    "edc": "https://w3id.org/edc/v0.0.1/ns/"
  },
  "@type": "https://w3id.org/edc/v0.0.1/ns/Secret",
  "@id": "{{ participant_did }}-{{ sts_key_name }}",
  "https://w3id.org/edc/v0.0.1/ns/value": "{{ client_secret }}"
}
"""

CREDENTIAL_PROPS_DATAPROCESSOR = """
{
  "claims": {
    "id": "{{ participant_did }}",
    "contractVersion": "1.0.0",
    "level": "processing"
  },
  "id": "{{ participant_did }}"
}
"""

CREDENTIAL_PROPS_MEMBERSHIP = """
{
  "claims": {
    "membership": {
      "membershipType": "FullMember",
      "website": "www.company-website.com",
      "contact": "max.mustermann@company.com",
      "since": "2023-05-08T00:00:00Z"
    }
  },
  "id": "{{ participant_did }}"
}
"""

class VcSaverService:

    def __init__(self):
      pass

    async def create_participant_and_save_vc(self, ctx: InsertVcRequest):
      logger.info(ctx.connector_did)
      
      try:
        participant_result = await self._create_participant_in_identity_hub(
          ctx.connector_did, 
          ctx.connector_dsp_url, 
          ctx.identity_hub_identity_url,
          ctx.identity_hub_credentials_url,
          ctx.identity_hub_api_key,
          ctx.sts_public_key_pem)
        
        logger.info(participant_result)

        await self._save_secret_in_connector(
          ctx.connector_did, participant_result, ctx.connector_management_url, ctx.connector_api_key)
        
      except HTTPException as e:
        if e.status_code == 409:
          logger.info(f"Participant {ctx.connector_did} already exists in IH")
          pass
      
      await self._store_credential_in_identity_hub(
        ctx.connector_did, [], ctx.identity_hub_identity_url, ctx.identity_hub_api_key)

    async def _create_participant_in_identity_hub(
        self, did, connector_dsp_url, identity_hub_identity_url, identity_hub_credentials_url, identity_hub_api_key, public_sts_key) -> dict:
      safe_pem = public_sts_key.strip().replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")

      url = f"{identity_hub_identity_url}/v1alpha/participants"
      headers = {"x-api-key": identity_hub_api_key, "Content-Type": "application/json"}

      participant_context_id_base64 = self._encode_participant_context_id(did)
      credential_service_endpoint = f"{identity_hub_credentials_url}/v1/participants/{participant_context_id_base64}"
      
      body = render_jinja_template(
        PARTICIPANT_DATA_TEMPLATE,
        {
          "credential_service_endpoint": credential_service_endpoint,
          "protocol_service_endpoint": connector_dsp_url,
          "participant_did": did,
          "pem_value": safe_pem
        })
      
      body = json.loads(body)
      logger.info(body)

      async with httpx.AsyncClient(timeout=10) as client:
          r = await client.post(url, headers=headers, json=body)
          if r.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail={"create_participant_error": r.text})
          if r.status_code == 409:
            return HTTPException(status_code=409, detail={"create_participant_error conflict": r.text})
          return r.json() if r.text else {}
      
    async def _save_secret_in_connector(self, did, participant_result, management_url, connector_api_key):
      url = f"{management_url}/v3/secrets"
      client_secret = participant_result["clientSecret"]
      headers = {"x-api-key": connector_api_key, "Content-Type": "application/json"}

      body = render_jinja_template(
        SECRETS_DATA_TEMPLATE,
        {
          "participant_did": did,
          "sts_key_name": "sts-client-secret",
          "client_secret": client_secret
        })
      
      body = json.loads(body)
      logger.info(body)

      async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, headers=headers, json=body)
        if r.status_code not in (200, 201, 409):
            raise HTTPException(status_code=502, detail={"_save_secret_in_connector_error": r.text})
      
      logger.info(r.json())
      return r.json() if r.text else {}
      
    async def _store_credential_in_identity_hub(self, participant_id: str, vcs, identity_hub_identity_url, identity_hub_api_key):
      participant_context_base64 = self._encode_participant_context_id(participant_id)
      
      url = f"{identity_hub_identity_url}/v1alpha/participants/{participant_context_base64}/credentials"
      headers = {"x-api-key": identity_hub_api_key, "Content-Type": "application/json"}

      vcs = await vc_generator_service.create_vc_set(GenerateVcRequest(
          connector_did=participant_id,
          vc_format="VC1_0_JWT",
          credential_type="MembershipCredential",
      ))

      for vc in vcs:

        logger.info(vc)

        async with httpx.AsyncClient(timeout=10) as client:
          r = await client.post(url, headers=headers, json=vc)
          if r.status_code not in (204, 409):
            raise HTTPException(status_code=502, detail={"store_credential_error": r.text})
      
    def _encode_participant_context_id(self, participant_id: str) -> str:
      # Base64-encode the exact participantId string used at creation time
      return base64.b64encode(participant_id.encode("utf-8")).decode("ascii")
    
vc_saver_service = VcSaverService()
