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

logger = setup_logging()

# should be saved in config
IH_API_KEY = 'c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo='

# should be passed from the request
PEM = """
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r
oYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==
-----END PUBLIC KEY-----
"""
CONNECTOR_API_KEY = 'password'

DATA_TEMPLATE = """
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

IDENTITY_HUB_ID = 'did:web:provider-ih'
IDENTITY_BASE = "http://provider-ih:7092/api/identity/v1alpha"

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

class CreateParticipantPayload:
  participant_context_id: str
  display_name: str
  did: str                   # did:web:example.com:participants:acme (example)
  participant_api_key: str   # you can generate it here or let IH return one
  # list of pre-issued VCs to seed (each item is either rawVc+format or a structured credential)
  seed_vcs: list[dict] = []  # e.g. [{"format":"VC1_0_JWT","rawVc":"<...>"}]

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

    async def create_participant_and_save_vc(self, ctx: CreateParticipantPayload):
      participant_id = f'{ctx.display_name}'
      did = f'{IDENTITY_HUB_ID}:{participant_id}'
      logger.info(did)
      
      participant_result = await self._create_participant_in_identity_hub(did)
      logger.info(participant_result)

      # not needed if connector and ih use the same KeyVault
      # await self._save_secret_in_connector(participant_result)
      await self._store_credential_in_identity_hub(did, IH_API_KEY, ctx.vc)

    async def _create_participant_in_identity_hub(self, did) -> dict:
      safe_pem = PEM.strip().replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")

      url = f"{IDENTITY_BASE}/participants"
      headers = {"x-api-key": IH_API_KEY, "Content-Type": "application/json"}
      body = render_jinja_template(
        DATA_TEMPLATE,
        {
          "credential_service_endpoint": "http://provider-ih:7091/api/credentials/v1/participants/ZGlkOndlYjpwcm92aWRlci1paCUzQTcwOTM6Ym9i",
          "protocol_service_endpoint": "http://provider-connector:8192/api/dsp",
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

      # TODO check if ok & correct
      logger.info(self.key_name)
      return VCResponse(username="user", vc={"key": "value"}, connector_token="token")
      
    async def _save_secret_in_connector(self, participant_result):
      url = f"http://provider-connector:8191/api/management/v3/secrets"
      client_secret = participant_result.clientSecret
      headers = {"x-api-key": CONNECTOR_API_KEY, "Content-Type": "application/json"}

      body = render_jinja_template(
        SECRETS_DATA_TEMPLATE,
        {
          "sts_key_name": "piotr-sts-client-secret",
          "client_secret": client_secret
        })
      
      body = json.loads(body)
      logger.info(body)

      async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, headers=headers, json=body)
        if r.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail={"_save_secret_in_connector_error": r.text})
      return r.json() if r.text else {}
      
    async def _store_credential_in_identity_hub(self, participant_id: str, participant_api_key: str, vc: dict):
      url = f"{IDENTITY_BASE}/participants/{self._encode_participant_context_id(participant_id)}/credentials"
      headers = {"x-api-key": participant_api_key, "Content-Type": "application/json"}
      # manifest
      body = {
        "participantContextId": participant_id,
        "verifiableCredentialContainer": {
           "credential": {
              "format": "VC1_0_JWT",
              "rawVc": vc["rawVc"],
              "credentialSubject": [
                {
                  "id": "did:web:provider-ih%3A7093:bob",
                  "claims": {
                    "id": "did:web:provider-ih%3A7093:bob",
                    "contractVersion": "1.0.0",
                    "level": "processing"
                  }
                }
              ],
              "id": "http://org.yourdataspace.com/credentials/1265",
              "type": [
                "VerifiableCredential",
                "DataProcessorCredential"
              ],
              "issuer": {
                "id": "did:web:dataspace-issuer",
                "additionalProperties": {}
              },
              "issuanceDate": 1702339200.0,
              "expirationDate": None,
              "credentialStatus": None,
              "description": None,
              "name": None
            }
          }
      }
      logger.info(body)

      async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, headers=headers, json=body)
        if r.status_code != 204:
            raise HTTPException(status_code=502, detail={"store_credential_error": r.text})
      
    def _encode_participant_context_id(self, participant_id: str) -> str:
      # Base64-encode the exact participantId string used at creation time
      return base64.b64encode(participant_id.encode("utf-8")).decode("ascii")
    
vc_service = VCService()
