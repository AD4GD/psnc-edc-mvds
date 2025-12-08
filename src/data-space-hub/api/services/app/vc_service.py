from datetime import datetime, timezone
from uuid import uuid4

# from fastapi import HTTPException, status
import jwt

# import httpx
from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings, ProjectSettings, VerifiableCredentialsSettings

# from api.models.db import IssuedCredentials, Participant
from api.exceptions.registration_service_exceptions import RecordNotFoundException
from api.models.dto.local import CredentialFormatEnum, PublicKeyType
from api.models.dto.requests import UserInfoVCRequest
from api.models.dto.responses import VCResponse
from api.services.clients import async_postgres_service, vault_service

# from api.services.helper import sha256_hex, sign_jwt_with_vault
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

    async def create_vc(self, req: UserInfoVCRequest) -> dict:
        # TODO check if ok & correct
        logger.info(self.key_name)
        public_key: PublicKeyType = vault_service.get_public_key(self.key_name)
        logger.info(public_key)

        # 1) Validation of incoming data
        print(req.participant_did)
        if not req.participant_did:
            raise RecordNotFoundException(message="participant_did is required", record_type="participant_did for VC", status_code=400)
        participant = await async_postgres_service.get_participant_by_did(req.participant_did)
        if not participant:
            raise RecordNotFoundException(
                message=f"Participant {req.participant_did} not found", record_type="participant", record_id=req.participant_did
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        print(datetime.fromisoformat(public_key["expiration_time"]).isoformat())
        credential_uuid = str(uuid4())

        # 2) Build VC payload (JWT style)

        # Optional JSON-LD VC template (unsigned) - will be saved as metadata and serves as base for vc
        jsonld_vc_membership = render_json_template_string(
            jsonld_vc_template,
            JsonLdDict(
                claims=req.participant_claims,
                context_for=membership_context_template,
                credential_id=f"{ProjectSettings.frontend_url}/credentials/" + credential_uuid,
                credential_schema=None,
                credential_status=None,
                contract_version=VerifiableCredentialsSettings.contract_version,
                description="Membership Credential for actions requiring identification of membership",
                issuer=VerifiableCredentialsSettings.vc_issuer_did,
                issuance_date_iso=now_iso,
                expiration_date_iso=public_key["expiration_time"],
                list_of_credential_types=["VerifiableCredential", "MembershipCredential"],
                name="Membership Credential",
                processing_level="processing",
                participant_did=f"did:web:{participant.did}",
            ),
        )
        proof_membership = render_json_template_string(
            proof_template,
            ProofDict(
                key_created_date_iso=public_key["creation_time"],
                raw_vc_jwt="to_be_filled_after_signing",  # TODO
                verification_method=f"{VerifiableCredentialsSettings.vc_issuer_did}#keys-1",  # TODO
            ),
        )
        jsonld_vc_membership.update({"proof": proof_membership.get("proof")})

        # TODO make hash
        vc_membership_payload = render_json_template_string(
            vc_to_sign_template,
            VCDict(
                issuer=ProjectSettings.issuer_did,
                participant_did=f"did:web:{participant.did}",
                issued_at=int(datetime.fromisoformat(now_iso).timestamp()),
                expires_at=int(datetime.fromisoformat(public_key["expiration_time"]).timestamp()),
                metadata_vc="",
                vc=jsonld_vc_membership,
            ),
        )
        print(vc_membership_payload)

        full_vc_membership_credential = render_json_template_string(
            full_credential_template,
            FullCredentialDict(
                credential_id=f"{ProjectSettings.frontend_url}/credentials/" + credential_uuid,
                credential_ld=jsonld_vc_membership,
                creation_timestamp=int(datetime.now(timezone.utc).timestamp()),
                issuer_did=VerifiableCredentialsSettings.vc_issuer_did,
                issuance_policy=None,
                raw_vc_jwt="to_be_filled_after_signing",  # TODO
                reissuance_policy=None,
                state=500,
                participant_did=f"did:web:{participant.did}",
                vc_format=CredentialFormatEnum.VC1_0_JWT,
            ),
        )
        print(full_vc_membership_credential)

        jsonld_vc_dataprocessor = render_json_template_string(
            jsonld_vc_template,
            JsonLdDict(
                claims=req.participant_claims,
                context_for=dataprocessor_context_template,
                credential_id=f"{ProjectSettings.frontend_url}/credentials/" + credential_uuid,
                credential_schema=None,
                credential_status=None,
                contract_version=VerifiableCredentialsSettings.contract_version,
                description="Dataprocessor Credential for actions requiring identification of dataprocessor",
                issuer=VerifiableCredentialsSettings.vc_issuer_did,
                issuance_date_iso=now_iso,
                expiration_date_iso=public_key["expiration_time"],
                list_of_credential_types=["VerifiableCredential", "DataProcessorCredential"],
                name="Dataprocessor Credential",
                processing_level="processing",
                participant_did=f"did:web:{participant.did}",
            ),
        )
        proof_dataprocessor = render_json_template_string(
            proof_template,
            ProofDict(
                key_created_date_iso=public_key["creation_time"],
                raw_vc_jwt="to_be_filled_after_signing",  # TODO
                verification_method=f"{VerifiableCredentialsSettings.vc_issuer_did}#keys-1",  # TODO
            ),
        )
        jsonld_vc_dataprocessor.update({"proof": proof_dataprocessor})

        vc_dataprocessor_payload = render_json_template_string(
            vc_to_sign_template,
            VCDict(
                issuer=ProjectSettings.issuer_did,
                participant_did=f"did:web:{participant.did}",
                issued_at=int(datetime.fromisoformat(now_iso).timestamp()),
                expires_at=int(datetime.fromisoformat(public_key["expiration_time"]).timestamp()),
                metadata_vc="",
                vc=jsonld_vc_dataprocessor,
            ),
        )

        full_vc_dataprocessor_credential = render_json_template_string(
            full_credential_template,
            FullCredentialDict(
                credential_id=f"{ProjectSettings.frontend_url}/credentials/" + credential_uuid,
                credential_ld=jsonld_vc_membership,
                creation_timestamp=int(datetime.now(timezone.utc).timestamp()),
                issuer_did=VerifiableCredentialsSettings.vc_issuer_did,
                issuance_policy=None,
                raw_vc_jwt="to_be_filled_after_signing",  # TODO
                reissuance_policy=None,
                state=500,
                participant_did=f"did:web:{participant.did}",
                vc_format=CredentialFormatEnum.VC1_0_JWT,
            ),
        )
        print(jsonld_vc_dataprocessor)
        print(vc_dataprocessor_payload)
        print(full_vc_dataprocessor_credential)
        print(public_key)

        vc_jwt = jwt.encode(vc_dataprocessor_payload, key=public_key["public_key"])
        print(vc_jwt)

        # Perform DB operations
        # Create issued_credential record

        return VCResponse(username="user", vc=[full_vc_membership_credential, full_vc_dataprocessor_credential], connector_token="token")


vc_service = VCService()
