# from datetime import datetime, timezone
# from uuid import uuid4

# import httpx
from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings

# from api.models.db import IssuedCredentials, Participant
from api.models.dto.requests import UserInfoVCRequest
from api.models.dto.responses import VCResponse
from api.services.clients import async_postgres_service, vault_service
import httpx
from fastapi import FastAPI, HTTPException
from api.templates.template_filler import render_jinja_template
import json
import base64
import time
from api.core.settings import IdentityHubSettings
from api.models.dto.requests import InsertVcRequest

logger = setup_logging()

# should be passed from the request
PEM = """
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r
oYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==
-----END PUBLIC KEY-----
"""
CONNECTOR_API_KEY = 'password'

PARTICIPANT_DATA_TEMPLATE = """
  {
    "roles":[],
    "serviceEndpoints":[
      {
        "type": "CredentialService",
        "serviceEndpoint": "{{ credential_service_endpoint }}",
        "id": "consumer-credentialservice-1"
      },
      {
        "type": "ProtocolEndpoint",
        "serviceEndpoint": "{{ protocol_service_endpoint }}",
        "id": "consumer-dsp"
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
  "@id": "{{ participant_did }}:{{ sts_key_name }}",
  "https://w3id.org/edc/v0.0.1/ns/value": "{{ client_secret }}"
}
"""

VC_MANIFEST_TEMPLATE = """
{
  "participantContextId": "{{ participant_context_id }}",
  "verifiableCredentialContainer": {
    "credential": {
        "format": "{{ vc_format }}",
        "rawVc": "{{ raw_vc }}",
        "credentialSubject": [
          {
            "id": "{{ participant_did }}",
            "claims": {
              "id": "{{ participant_did }}",
              "contractVersion": "1.0.0",
              "level": "processing"
            }
          }
        ],
        "id": "http://org.yourdataspace.com/credentials/1265",
        "type": [
          "VerifiableCredential",
          "{{ credential_type }}"
        ],
        "issuer": {
          "id": "{{ issuer_did }}",
          "additionalProperties": {}
        },
        "issuanceDate": "{{ issuance_date }}",
        "expirationDate": null,
        "credentialStatus": null,
        "description": null,
        "name": null
      }
    }
}
"""

class VCService:
    """
    Full user registration flow:
      - validate request
      - verify participant exists
      - create registration_request (hashed token) for audit
      - build VC (JWT-VC and JSON-LD template)
      - sign JWT-VC via Vault Transit
      - create issued_credential record
      - POST VC + form + token back to connector (callback)
      - commit DB transaction only after successful callback (atomic)
    """

    def __init__(self):
      pass

    async def create_participant_and_save_vc(self, ctx: InsertVcRequest):
      participant_id = f'{ctx.participant_context_id}'
      did = f'{IdentityHubSettings.identity_hub_did}:{participant_id}'
      logger.info(did)
      
      participant_result = await self._create_participant_in_identity_hub(did, ctx.connector_dsp_url, ctx.public_sts_key)
      logger.info(participant_result)

      # not needed if connector and ih use the same KeyVault
      await self._save_secret_in_connector(did, participant_result, ctx.connector_management_url, ctx.connector_api_key)
      
      await self._store_credential_in_identity_hub(did, ctx.seed_vcs)

    async def _create_participant_in_identity_hub(self, did, connector_dsp_url, public_sts_key) -> dict:
      safe_pem = public_sts_key.strip().replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")

      url = f"{IdentityHubSettings.identity_api_url}/v1alpha/participants"
      headers = {"x-api-key": IdentityHubSettings.api_key, "Content-Type": "application/json"}

      participant_context_id_base64 = self._encode_participant_context_id(did)
      credential_service_endpoint = f"{IdentityHubSettings.credentials_api_url}/v1alpha/participants/{participant_context_id_base64}"
      
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
        if r.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail={"_save_secret_in_connector_error": r.text})
      
      logger.info(r.json())
      return r.json() if r.text else {}
      
    async def _store_credential_in_identity_hub(self, participant_id: str, vcs: list[dict]):
      participant_context_base64 = self._encode_participant_context_id(participant_id)
      
      url = f"{IdentityHubSettings.identity_api_url}/v1alpha/participants/{participant_context_base64}/credentials"
      headers = {"x-api-key": IdentityHubSettings.api_key, "Content-Type": "application/json"}

      for vc in vcs:
        # manifest
        body = render_jinja_template(
          VC_MANIFEST_TEMPLATE,
          {
            "participant_context_id": participant_id,
            "raw_vc": vc["rawVc"],
            "issuer_did": "did:web:dataspace-issuer",
            "issuance_date": time.time(),
            "vc_format": vc["format"],
            "credential_type": vc["credential_type"]
          })
        
        body = json.loads(body)
        logger.info(body)

        async with httpx.AsyncClient(timeout=10) as client:
          r = await client.post(url, headers=headers, json=body)
          if r.status_code != 204:
            raise HTTPException(status_code=502, detail={"store_credential_error": r.text})
      
    def _encode_participant_context_id(self, participant_id: str) -> str:
      # Base64-encode the exact participantId string used at creation time
      return base64.b64encode(participant_id.encode("utf-8")).decode("ascii")
    
vc_service = VCService()
