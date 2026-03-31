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


class VcSaverService:

    def __init__(self):
      pass

    async def issue_and_store_vcs(self, ctx: InsertVcRequest):
      """
      Generate VCs for a participant and store them in the Identity Hub.
      
      Participant context creation in IH and STS secret storage in the
      connector are now handled externally by the init-dataspace script.
      """
      logger.info(f"Issuing VCs for {ctx.connector_did}")

      await self._store_credential_in_identity_hub(
        ctx.connector_did, [], ctx.identity_hub_identity_url, ctx.identity_hub_api_key)

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
