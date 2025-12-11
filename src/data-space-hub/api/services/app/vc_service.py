from datetime import datetime, timezone
from uuid import uuid4

from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings, ProjectSettings, VerifiableCredentialsSettings
from api.exceptions.registration_service_exceptions import RecordNotFoundException
from api.models.dto.local import CredentialFormatEnum, PublicKeyType
from api.models.dto.requests import VCRequest
from api.models.dto.responses import VCResponse
from api.services.clients import async_postgres_service, vault_service
from api.templates.credentials import (
    dataprocessor_context_template,
    full_credential_template,
    jsonld_vc_template,
    membership_context_template,
    proof_template,
    vc_to_sign_template,
)
from api.templates.dict_templates import FullCredentialDict, JsonLdDict, ProofDict, VCDict
from api.templates.template_filler import render_json_template_string

logger = setup_logging()


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
        self.postgres = async_postgres_service
        self.vault = vault_service
        # transit key name and jwt alg from settings
        self.key_name = getattr(KeyVaultSettings, "key_name", "key_name")
        self.jwt_alg = getattr(KeyVaultSettings, "rs_jwt_alg", "RS256")

    async def create_vc(self, req: VCRequest) -> dict:
        # TODO check if ok & correct
        if not req.connector_did:
            raise RecordNotFoundException(message="connector_did is required", record_type="connector_did for VC", status_code=400)
        connector = await async_postgres_service.get_connector_by_did(req.connector_did)
        if not connector:
            raise RecordNotFoundException(message=f"Connector {req.connector_did} not found", record_type="connector", record_id=req.connector_did)

        public_key: PublicKeyType = vault_service.get_public_key(self.key_name)
        now_iso = datetime.now(timezone.utc).isoformat()
        credential_uuid = str(uuid4())
        verification_method = f"{VerifiableCredentialsSettings.vc_issuer_did}#key-{public_key['version']}"

        jsonld_vc = render_json_template_string(
            jsonld_vc_template,
            JsonLdDict(
                claims=req.claims,
                context_for=membership_context_template if req.vc_type == "membership" else dataprocessor_context_template,
                credential_id=f"{ProjectSettings.frontend_url}/credentials/" + credential_uuid,
                credential_schema=None,
                credential_status=None,
                contract_version=VerifiableCredentialsSettings.contract_version,
                description="Membership Credential for actions requiring identification of membership",
                issuer=VerifiableCredentialsSettings.vc_issuer_did,
                issuance_date_iso=now_iso,
                expiration_date_iso=public_key["expiration_time"],
                list_of_credential_types=["VerifiableCredential", "MembershipCredential"]
                if req.vc_type == "membership"
                else ["VerifiableCredential", "DataProcessorCredential"],
                name="Membership Credential"
                if req.vc_type == "membership"
                else "Data Processor Credential"
                if req.vc_type == "dataprocessor"
                else "Credential",
                processing_level="processing",
                connector_did=f"{connector.did}",
            ),
        )

        vc_payload = render_json_template_string(
            vc_to_sign_template,
            VCDict(
                issuer=ProjectSettings.issuer_did,
                connector_did=f"{connector.did}",
                issued_at=int(datetime.fromisoformat(now_iso).timestamp()),
                expires_at=int(datetime.fromisoformat(public_key["expiration_time"]).timestamp()),
                metadata_vc="",
                vc=jsonld_vc,
            ),
        )
        token = await vault_service.make_jwt(vc_payload, key_name=self.key_name, verification_method=verification_method)

        proof = render_json_template_string(
            proof_template,
            ProofDict(
                key_created_date_iso=public_key["creation_time"],
                raw_vc_jwt=token,
                verification_method=verification_method,
            ),
        )
        jsonld_vc.update({"proof": proof.get("proof")})

        full_vc_credential = render_json_template_string(
            full_credential_template,
            FullCredentialDict(
                credential_id=f"{ProjectSettings.frontend_url}/credentials/" + credential_uuid,
                credential_ld=jsonld_vc,
                creation_timestamp=int(datetime.now(timezone.utc).timestamp()),
                issuer_did=VerifiableCredentialsSettings.vc_issuer_did,
                issuance_policy=None,
                raw_vc_jwt=token,
                reissuance_policy=None,
                state=500,
                connector_did=f"{connector.did}",
                vc_format=CredentialFormatEnum.VC1_0_JWT,
            ),
        )

        # Perform DB operations
        # Create issued_credential record

        return VCResponse(vc=full_vc_credential, type=req.vc_type, connector_token="token")


vc_service = VCService()
