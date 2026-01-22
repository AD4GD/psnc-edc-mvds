from datetime import datetime, timezone
from uuid import uuid4

from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings, ProjectSettings, VerifiableCredentialsSettings
from api.exceptions.registration_service_exceptions import RecordNotFoundException
from api.models.dto.local import CredentialFormatEnum, PublicKeyType
from api.models.dto.requests import GenerateVcRequest
from api.models.dto.responses import VCResponse
from api.services.clients import async_postgres_service, vault_service
from api.templates.credentials import (
    dataprocessor_context_template,
    full_credential_template,
    jsonld_vc_template,
    jsonld_vc_credential_template,
    membership_context_template,
    proof_template,
    vc_to_sign_template,
)
from api.templates.dict_templates import FullCredentialDict, JsonLdDict, ProofDict, VCDict
from api.templates.template_filler import render_json_template_string
import json

logger = setup_logging()

CREDENTIAL_PROPS_DATAPROCESSOR = """
{
  "claims": {
    "id": {participant_did},
    "contractVersion": "1.0.0",
    "level": "processing"
  },
  "id": {participant_did}
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
  "id": {participant_did}
}
"""

class VcGeneratorService:
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
        self.postgres = async_postgres_service
        self.vault = vault_service
        # transit key name and jwt alg from settings
        self.key_name = getattr(KeyVaultSettings, "key_name", "key_name")
        self.jwt_alg = getattr(KeyVaultSettings, "rs_jwt_alg", "RS256")

    async def get_raw_vc(self, req: GenerateVcRequest, credential, verification_method, now_iso) -> str:
        
        vc = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/security/suites/jws-2020/v1",
                "https://www.w3.org/ns/did/v1",
                {
                    "mvd-credentials": "https://w3id.org/mvd/credentials/",
                    "membership": "mvd-credentials:membership",
                    "membershipType": "mvd-credentials:membershipType",
                    "website": "mvd-credentials:website",
                    "contact": "mvd-credentials:contact",
                    "since": "mvd-credentials:since"
                }
            ],
            **credential
        }

        issuer = vc.get("issuer")
        vc["issuer"] = issuer.get("id")

        cs = vc.get("credentialSubject")
        entry = cs[0]

        subject_id = entry.get("id")
        claims = entry.get("claims", {})

        vc["credentialSubject"] = {
            "id": subject_id,
            **claims
        }

        vc = {k: v for k, v in vc.items() if v is not None}

        claims = {
            "iss": VerifiableCredentialsSettings.vc_issuer_did, 
            "sub": req.connector_did, 
            "aud": req.connector_did, 
            "iat": int(datetime.now(timezone.utc).timestamp()), 
            "vc": vc
        }
        token = await vault_service.make_jwt(claims, key_name=self.key_name, verification_method=verification_method)

        return token

    async def create_vc_set(self, req: GenerateVcRequest) -> list[dict]:

        public_key: PublicKeyType = vault_service.get_public_key(self.key_name)
        now_iso = datetime.now(timezone.utc)
        now_iso = now_iso.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        
        credential_uuid = str(uuid4())
        verification_method = f"{VerifiableCredentialsSettings.vc_issuer_did}#key-{public_key['version']}"

        generated_vcs = []
        for credential_type in ["MembershipCredential", "DataProcessorCredential"]:

            cred_props = None

            if (credential_type == "MembershipCredential"):
                cred_props = CREDENTIAL_PROPS_MEMBERSHIP
            else:
                cred_props = CREDENTIAL_PROPS_DATAPROCESSOR
            cred_props_json = render_json_template_string(
                cred_props,
                JsonLdDict(
                    participant_did=req.connector_did
                ))

            vc_credential_str = render_json_template_string(
                jsonld_vc_credential_template,
                JsonLdDict(
                    credential_props=cred_props_json,
                    credential_type=credential_type,
                    issuer_did=VerifiableCredentialsSettings.vc_issuer_did,
                    issuance_date=now_iso
                ),
            )

            raw_vc = await self.get_raw_vc(req, vc_credential_str, verification_method, now_iso)

            jsonld_vc_manifest_str = render_json_template_string(
                jsonld_vc_template,
                JsonLdDict(
                    participant_context_id=req.connector_did,
                    vc_format=req.vc_format,
                    raw_vc=raw_vc,
                    credential=vc_credential_str
                ),
            )

            generated_vcs.append(jsonld_vc_manifest_str)

        # Perform DB operations
        # Create issued_credential record

        return generated_vcs


vc_generator_service = VcGeneratorService()
