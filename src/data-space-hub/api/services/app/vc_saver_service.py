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
from api.services.app import vc_generator_service

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
  "@id": "{{ participant_did }}-{{ sts_key_name }}",
  "https://w3id.org/edc/v0.0.1/ns/value": "{{ client_secret }}"
}
"""

VC_MANIFEST_TEMPLATE = """
{
  "participantContextId": "{{ participant_context_id }}",
  "verifiableCredentialContainer": {
    "format": "{{ vc_format }}",
    "rawVc": "{{ raw_vc }}",
    "credential": {
        "credentialSubject": [
          {{ credential_props }}
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
      
      await self._store_credential_in_identity_hub(
        ctx.connector_did, ctx.generated_vcs, ctx.identity_hub_identity_url, ctx.identity_hub_api_key)

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
          if r.status_code not in (200, 201, 409):
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

      #vcs = self._get_example_vcs(participant_id)

      for vc in vcs:

        logger.info(vc)

        async with httpx.AsyncClient(timeout=10) as client:
          r = await client.post(url, headers=headers, json=vc)
          if r.status_code not in (204, 409):
            raise HTTPException(status_code=502, detail={"store_credential_error": r.text})
      
    def _encode_participant_context_id(self, participant_id: str) -> str:
      # Base64-encode the exact participantId string used at creation time
      return base64.b64encode(participant_id.encode("utf-8")).decode("ascii")
    
    def _get_example_vcs(self, did: str):

      vc_requests = []

      if ("fc" in did):
        vc_requests = [
          {
            "format": "VC1_0_JWT",
            "credential_type": "MembershipCredential", 
            "rawVc": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciNrZXktMSJ9.eyJpc3MiOiJkaWQ6d2ViOmRhdGFzcGFjZS1pc3N1ZXIiLCJzdWIiOiJkaWQ6d2ViOmZjLWloJTNBNzEwMzpwaW90ciIsImF1ZCI6ImRpZDp3ZWI6ZmMtaWglM0E3MTAzOnBpb3RyIiwiaWF0IjoxNzYwMDI1MjkzLCJ2YyI6eyJAY29udGV4dCI6WyJodHRwczovL3d3dy53My5vcmcvMjAxOC9jcmVkZW50aWFscy92MSIsImh0dHBzOi8vdzNpZC5vcmcvc2VjdXJpdHkvc3VpdGVzL2p3cy0yMDIwL3YxIiwiaHR0cHM6Ly93d3cudzMub3JnL25zL2RpZC92MSIseyJtdmQtY3JlZGVudGlhbHMiOiJodHRwczovL3czaWQub3JnL212ZC9jcmVkZW50aWFscy8iLCJtZW1iZXJzaGlwIjoibXZkLWNyZWRlbnRpYWxzOm1lbWJlcnNoaXAiLCJtZW1iZXJzaGlwVHlwZSI6Im12ZC1jcmVkZW50aWFsczptZW1iZXJzaGlwVHlwZSIsIndlYnNpdGUiOiJtdmQtY3JlZGVudGlhbHM6d2Vic2l0ZSIsImNvbnRhY3QiOiJtdmQtY3JlZGVudGlhbHM6Y29udGFjdCIsInNpbmNlIjoibXZkLWNyZWRlbnRpYWxzOnNpbmNlIn1dLCJpZCI6Imh0dHA6Ly9vcmcueW91cmRhdGFzcGFjZS5jb20vY3JlZGVudGlhbHMvMjM0NyIsInR5cGUiOlsiVmVyaWZpYWJsZUNyZWRlbnRpYWwiLCJNZW1iZXJzaGlwQ3JlZGVudGlhbCJdLCJpc3N1ZXIiOiJkaWQ6d2ViOmRhdGFzcGFjZS1pc3N1ZXIiLCJpc3N1YW5jZURhdGUiOiIyMDIzLTA4LTE4VDAwOjAwOjAwWiIsImNyZWRlbnRpYWxTdWJqZWN0Ijp7ImlkIjoiZGlkOndlYjpmYy1paCUzQTcxMDM6cGlvdHIiLCJtZW1iZXJzaGlwIjp7Im1lbWJlcnNoaXBUeXBlIjoiRnVsbE1lbWJlciIsIndlYnNpdGUiOiJ3d3cud2hhdGV2ZXIuY29tIiwiY29udGFjdCI6Im1peC5tYXhAd2hhdGV2ZXIuY29tIiwic2luY2UiOiIyMDIzLTAxLTAxVDAwOjAwOjAwWiJ9fX19.lHuzqFi0a9jqSsEnwsTtBfgP2uvRB6SbHjH7m9-sqeWG9KyrXKgMQUE7gMcshS7K9h3hkJk0siQq1JXAkwkDAw"
          },
          {
            "format": "VC1_0_JWT",
            "credential_type": "DataProcessorCredential", 
            "rawVc": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciNrZXktMSJ9.eyJpc3MiOiJkaWQ6d2ViOmRhdGFzcGFjZS1pc3N1ZXIiLCJzdWIiOiJkaWQ6d2ViOmZjLWloJTNBNzEwMzpwaW90ciIsImF1ZCI6ImRpZDp3ZWI6ZmMtaWglM0E3MTAzOnBpb3RyIiwiaWF0IjoxNzYwMDI1MjkzLCJ2YyI6eyJAY29udGV4dCI6WyJodHRwczovL3d3dy53My5vcmcvMjAxOC9jcmVkZW50aWFscy92MSIsImh0dHBzOi8vdzNpZC5vcmcvc2VjdXJpdHkvc3VpdGVzL2p3cy0yMDIwL3YxIiwiaHR0cHM6Ly93d3cudzMub3JnL25zL2RpZC92MSIseyJtdmQtY3JlZGVudGlhbHMiOiJodHRwczovL3czaWQub3JnL212ZC9jcmVkZW50aWFscy8iLCJjb250cmFjdFZlcnNpb24iOiJtdmQtY3JlZGVudGlhbHM6Y29udHJhY3RWZXJzaW9uIiwibGV2ZWwiOiJtdmQtY3JlZGVudGlhbHM6bGV2ZWwifV0sImlkIjoiaHR0cDovL29yZy55b3VyZGF0YXNwYWNlLmNvbS9jcmVkZW50aWFscy8yMzQ3IiwidHlwZSI6WyJWZXJpZmlhYmxlQ3JlZGVudGlhbCIsIkRhdGFQcm9jZXNzb3JDcmVkZW50aWFsIl0sImlzc3VlciI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciIsImlzc3VhbmNlRGF0ZSI6IjIwMjMtMDgtMThUMDA6MDA6MDBaIiwiY3JlZGVudGlhbFN1YmplY3QiOnsiaWQiOiJkaWQ6d2ViOmZjLWloJTNBNzEwMzpwaW90ciIsImxldmVsIjoicHJvY2Vzc2luZyIsImNvbnRyYWN0VmVyc2lvbiI6IjEuMC4wIn19fQ.kTLTX3VlDeC7AMP-MLQJK_UXnfK3_D4G9fOAa9gp9lvETvBXq6m6Alt69T94PjQJDTdDVJBUPAysKShA0l2yAw"
          }
        ]
      elif ("consumer" in did):
        vc_requests = [
          {
            "format": "VC1_0_JWT",
            "credential_type": "MembershipCredential", 
            "rawVc": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciNrZXktMSJ9.eyJpc3MiOiJkaWQ6d2ViOmRhdGFzcGFjZS1pc3N1ZXIiLCJzdWIiOiJkaWQ6d2ViOmNvbnN1bWVyLWloJTNBNzA4MzphbGljZSIsImF1ZCI6ImRpZDp3ZWI6Y29uc3VtZXItaWglM0E3MDgzOmFsaWNlIiwiaWF0IjoxNzYwMDI1MjkzLCJ2YyI6eyJAY29udGV4dCI6WyJodHRwczovL3d3dy53My5vcmcvMjAxOC9jcmVkZW50aWFscy92MSIsImh0dHBzOi8vdzNpZC5vcmcvc2VjdXJpdHkvc3VpdGVzL2p3cy0yMDIwL3YxIiwiaHR0cHM6Ly93d3cudzMub3JnL25zL2RpZC92MSIseyJtdmQtY3JlZGVudGlhbHMiOiJodHRwczovL3czaWQub3JnL212ZC9jcmVkZW50aWFscy8iLCJtZW1iZXJzaGlwIjoibXZkLWNyZWRlbnRpYWxzOm1lbWJlcnNoaXAiLCJtZW1iZXJzaGlwVHlwZSI6Im12ZC1jcmVkZW50aWFsczptZW1iZXJzaGlwVHlwZSIsIndlYnNpdGUiOiJtdmQtY3JlZGVudGlhbHM6d2Vic2l0ZSIsImNvbnRhY3QiOiJtdmQtY3JlZGVudGlhbHM6Y29udGFjdCIsInNpbmNlIjoibXZkLWNyZWRlbnRpYWxzOnNpbmNlIn1dLCJpZCI6Imh0dHA6Ly9vcmcueW91cmRhdGFzcGFjZS5jb20vY3JlZGVudGlhbHMvMjM0NyIsInR5cGUiOlsiVmVyaWZpYWJsZUNyZWRlbnRpYWwiLCJNZW1iZXJzaGlwQ3JlZGVudGlhbCJdLCJpc3N1ZXIiOiJkaWQ6d2ViOmRhdGFzcGFjZS1pc3N1ZXIiLCJpc3N1YW5jZURhdGUiOiIyMDIzLTA4LTE4VDAwOjAwOjAwWiIsImNyZWRlbnRpYWxTdWJqZWN0Ijp7ImlkIjoiZGlkOndlYjpjb25zdW1lci1paCUzQTcwODM6YWxpY2UiLCJtZW1iZXJzaGlwIjp7Im1lbWJlcnNoaXBUeXBlIjoiRnVsbE1lbWJlciIsIndlYnNpdGUiOiJ3d3cud2hhdGV2ZXIuY29tIiwiY29udGFjdCI6ImZpenouYnV6ekB3aGF0ZXZlci5jb20iLCJzaW5jZSI6IjIwMjMtMDEtMDFUMDA6MDA6MDBaIn19fX0.dsck9uvN8D02nrK51D4y-uMaJ7L17Gl_gIoecF0TaXHVUv1zlb5ZLXRH1bm85p0IYd4rOJ1hfTmqhbHNWRD7Bg"
          },
          {
            "format": "VC1_0_JWT",
            "credential_type": "DataProcessorCredential", 
            "rawVc": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciNrZXktMSJ9.eyJpc3MiOiJkaWQ6d2ViOmRhdGFzcGFjZS1pc3N1ZXIiLCJzdWIiOiJkaWQ6d2ViOmNvbnN1bWVyLWloJTNBNzA4MzphbGljZSIsImF1ZCI6ImRpZDp3ZWI6Y29uc3VtZXItaWglM0E3MDgzOmFsaWNlIiwiaWF0IjoxNzYwMDI1MjkzLCJ2YyI6eyJAY29udGV4dCI6WyJodHRwczovL3d3dy53My5vcmcvMjAxOC9jcmVkZW50aWFscy92MSIsImh0dHBzOi8vdzNpZC5vcmcvc2VjdXJpdHkvc3VpdGVzL2p3cy0yMDIwL3YxIiwiaHR0cHM6Ly93d3cudzMub3JnL25zL2RpZC92MSIseyJtdmQtY3JlZGVudGlhbHMiOiJodHRwczovL3czaWQub3JnL212ZC9jcmVkZW50aWFscy8iLCJjb250cmFjdFZlcnNpb24iOiJtdmQtY3JlZGVudGlhbHM6Y29udHJhY3RWZXJzaW9uIiwibGV2ZWwiOiJtdmQtY3JlZGVudGlhbHM6bGV2ZWwifV0sImlkIjoiaHR0cDovL29yZy55b3VyZGF0YXNwYWNlLmNvbS9jcmVkZW50aWFscy8yMzQ3IiwidHlwZSI6WyJWZXJpZmlhYmxlQ3JlZGVudGlhbCIsIkRhdGFQcm9jZXNzb3JDcmVkZW50aWFsIl0sImlzc3VlciI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciIsImlzc3VhbmNlRGF0ZSI6IjIwMjMtMDgtMThUMDA6MDA6MDBaIiwiY3JlZGVudGlhbFN1YmplY3QiOnsiaWQiOiJkaWQ6d2ViOmNvbnN1bWVyLWloJTNBNzA4MzphbGljZSIsImNvbnRyYWN0VmVyc2lvbiI6IjEuMC4wIiwibGV2ZWwiOiJwcm9jZXNzaW5nIn19fQ.Tke8ZX_2PaJHq3VI8G9W02GezOZXYkuRynyuATk0EDbUlOKqPjSWQfNO87tloYWW4ZY2vsSNSYIV2WYtR70QCw"
          }
        ]
      elif ("provider" in did):
        vc_requests = [
          {
            "format": "VC1_0_JWT",
            "credential_type": "MembershipCredential", 
            "rawVc": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciNrZXktMSJ9.eyJpc3MiOiJkaWQ6d2ViOmRhdGFzcGFjZS1pc3N1ZXIiLCJzdWIiOiJkaWQ6d2ViOnByb3ZpZGVyLWloJTNBNzA5Mzpib2IiLCJhdWQiOiJkaWQ6d2ViOnByb3ZpZGVyLWloJTNBNzA5Mzpib2IiLCJpYXQiOjE3NjAwMjUyOTMsInZjIjp7IkBjb250ZXh0IjpbImh0dHBzOi8vd3d3LnczLm9yZy8yMDE4L2NyZWRlbnRpYWxzL3YxIiwiaHR0cHM6Ly93M2lkLm9yZy9zZWN1cml0eS9zdWl0ZXMvandzLTIwMjAvdjEiLCJodHRwczovL3d3dy53My5vcmcvbnMvZGlkL3YxIix7Im12ZC1jcmVkZW50aWFscyI6Imh0dHBzOi8vdzNpZC5vcmcvbXZkL2NyZWRlbnRpYWxzLyIsIm1lbWJlcnNoaXAiOiJtdmQtY3JlZGVudGlhbHM6bWVtYmVyc2hpcCIsIm1lbWJlcnNoaXBUeXBlIjoibXZkLWNyZWRlbnRpYWxzOm1lbWJlcnNoaXBUeXBlIiwid2Vic2l0ZSI6Im12ZC1jcmVkZW50aWFsczp3ZWJzaXRlIiwiY29udGFjdCI6Im12ZC1jcmVkZW50aWFsczpjb250YWN0Iiwic2luY2UiOiJtdmQtY3JlZGVudGlhbHM6c2luY2UifV0sImlkIjoiaHR0cDovL29yZy55b3VyZGF0YXNwYWNlLmNvbS9jcmVkZW50aWFscy8yMzQ3IiwidHlwZSI6WyJWZXJpZmlhYmxlQ3JlZGVudGlhbCIsIk1lbWJlcnNoaXBDcmVkZW50aWFsIl0sImlzc3VlciI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciIsImlzc3VhbmNlRGF0ZSI6IjIwMjMtMDgtMThUMDA6MDA6MDBaIiwiY3JlZGVudGlhbFN1YmplY3QiOnsiaWQiOiJkaWQ6d2ViOnByb3ZpZGVyLWloJTNBNzA5Mzpib2IiLCJtZW1iZXJzaGlwIjp7Im1lbWJlcnNoaXBUeXBlIjoiRnVsbE1lbWJlciIsIndlYnNpdGUiOiJ3d3cud2hhdGV2ZXIuY29tIiwiY29udGFjdCI6Im1peC5tYXhAd2hhdGV2ZXIuY29tIiwic2luY2UiOiIyMDIzLTAxLTAxVDAwOjAwOjAwWiJ9fX19.I4AL41LLy-Kv67JfP-gN68p084-I3a293Kfth7_wroYYAb0t2nK02DajssMAn5VHnSYD9ZjyqdDu6DunC240AA"
          },
          {
            "format": "VC1_0_JWT",
            "credential_type": "DataProcessorCredential", 
            "rawVc": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZDp3ZWI6ZGF0YXNwYWNlLWlzc3VlciNrZXktMSJ9.eyJpc3MiOiJkaWQ6d2ViOmRhdGFzcGFjZS1pc3N1ZXIiLCJzdWIiOiJkaWQ6d2ViOnByb3ZpZGVyLWloJTNBNzA5Mzpib2IiLCJhdWQiOiJkaWQ6d2ViOnByb3ZpZGVyLWloJTNBNzA5Mzpib2IiLCJpYXQiOjE3NjAwMjUyOTMsInZjIjp7IkBjb250ZXh0IjpbImh0dHBzOi8vd3d3LnczLm9yZy8yMDE4L2NyZWRlbnRpYWxzL3YxIiwiaHR0cHM6Ly93M2lkLm9yZy9zZWN1cml0eS9zdWl0ZXMvandzLTIwMjAvdjEiLCJodHRwczovL3d3dy53My5vcmcvbnMvZGlkL3YxIix7Im12ZC1jcmVkZW50aWFscyI6Imh0dHBzOi8vdzNpZC5vcmcvbXZkL2NyZWRlbnRpYWxzLyIsImNvbnRyYWN0VmVyc2lvbiI6Im12ZC1jcmVkZW50aWFsczpjb250cmFjdFZlcnNpb24iLCJsZXZlbCI6Im12ZC1jcmVkZW50aWFsczpsZXZlbCJ9XSwiaWQiOiJodHRwOi8vb3JnLnlvdXJkYXRhc3BhY2UuY29tL2NyZWRlbnRpYWxzLzIzNDciLCJ0eXBlIjpbIlZlcmlmaWFibGVDcmVkZW50aWFsIiwiRGF0YVByb2Nlc3NvckNyZWRlbnRpYWwiXSwiaXNzdWVyIjoiZGlkOndlYjpkYXRhc3BhY2UtaXNzdWVyIiwiaXNzdWFuY2VEYXRlIjoiMjAyMy0wOC0xOFQwMDowMDowMFoiLCJjcmVkZW50aWFsU3ViamVjdCI6eyJpZCI6ImRpZDp3ZWI6cHJvdmlkZXItaWglM0E3MDkzOmJvYiIsImxldmVsIjoicHJvY2Vzc2luZyIsImNvbnRyYWN0VmVyc2lvbiI6IjEuMC4wIn19fQ.meLs_PMiSnBAnc4yvKsPK5tx3RClQ7J8XRdaJ_HpNf0iogdLkqBWUm_sA62qKl7Jg4t4ANwMRKkowjSXMNDCCQ"
          }
        ]

      generated_vcs = []

      for vc_request in vc_requests:

        credential_props = None

        if vc_request['credential_type'] == 'MembershipCredential':
          credential_props = CREDENTIAL_PROPS_MEMBERSHIP
        else:
          credential_props = CREDENTIAL_PROPS_DATAPROCESSOR

        credential_props = render_jinja_template(
          credential_props,
          {
            "participant_did": did
          })
        logger.info(credential_props)
          
        # manifest
        body = render_jinja_template(
          VC_MANIFEST_TEMPLATE,
          {
            "participant_context_id": did,
            "raw_vc": vc_request["rawVc"],
            "issuer_did": "did:web:dataspace-issuer",
            "issuance_date": time.time(),
            "vc_format": vc_request["format"],
            "credential_type": vc_request["credential_type"],
            "credential_props": credential_props
          })
        
        body = json.loads(body)

        generated_vcs.append(body)
      
      return generated_vcs
    
vc_saver_service = VcSaverService()
