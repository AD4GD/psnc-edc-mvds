from datetime import datetime, timezone
from uuid import uuid4

import httpx
from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings, ProjectSettings
from api.models.db import IssuedCredentials, Participant
from api.models.dto.responses import SimpleMessageResponse
from api.models.dto.requests import UserInfoVCRequest
from api.services.clients import async_postgres_service, vault_service
from api.services.helper import sha256_hex, sign_jwt_with_vault
from api.templates.credentials.jsonld_vc import template as jsonld_vc_template
from api.templates.credentials.vc_to_sign import template as vc_to_sign_template
from api.templates.dict_templates import JsonLdDict, VCDict
from api.templates.template_filler import render_json_template_string
from fastapi import HTTPException, status

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
        self.key_name = getattr(KeyVaultSettings, "rs_transit_key_name", "rs-signing-key")
        self.jwt_alg = getattr(KeyVaultSettings, "rs_jwt_alg", "RS256")

    async def create_vc(self, req: UserInfoVCRequest) -> dict:
        # TODO check if ok & correct

        # 1) Validation of incoming data
        print(req.participant_did)
        if not req.participant_did:
            # Flow to add to main node (public one)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="participant_did is required")
        participant = await async_postgres_service.get_participant_by_did(req.participant_did)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant (connector) not found")

        now_ts = int(datetime.now(timezone.utc).timestamp())
        credential_uuid = str(uuid4())
        print(credential_uuid)

        # 2) Build VC payload (JWT style)

        # Optional JSON-LD VC template (unsigned) - will be saved as metadata and serves as base for vc
        try:
            jsonld_vc = render_json_template_string(
                jsonld_vc_template,
                JsonLdDict(
                    credential_id=f"{ProjectSettings.frontend_url}/credentials/" + credential_uuid,
                    issuer=ProjectSettings.issuer_did,
                    user_did="",
                    issuance_date_iso=now_ts,
                    expiration_date_iso=now_ts + 3600,
                    processing_level="processing",
                    contract_version="1.0.0",
                    claims=[{"k": "v"}],
                    alumniOf=None,
                ),
            )
            vc_payload = render_json_template_string(
                vc_to_sign_template,
                VCDict(
                    issuer=ProjectSettings.issuer_did,
                    user_did="",
                    issued_at=now_ts,
                    expires_at=now_ts + 3600,
                    metadata_vc="",
                    vc=sign_jwt_with_vault(jsonld_vc),
                ),
            )
            print(jsonld_vc)
            print(vc_payload)
        except Exception as e:
            logger.warning(str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        return [jsonld_vc, vc_payload]

        sub = req.user_claims.get("sub") or req.user_claims.get("email") or f"user:{uuid4()}"
        vc_payload = {
            "iss": ProjectSettings.issuer_did,  # issuer id / DID
            "aud": f"did:web:{participant.did}",
            "sub": sub,
            "iat": now_ts,
            "nbf": now_ts,
            "exp": now_ts + (req.ttl_seconds or 3600),
            "vc": {
                "type": ["VerifiableCredential", "UserRegistrationCredential"],
                "credentialSubject": req.user_claims,
            },
            "metadata": {
                "credential_id": credential_uuid,
                "issued_by": ProjectSettings.issuer_did,
            },
        }

        # 3) Sign JWT-VC using Vault (async helper sign_jwt_with_vault)
        try:
            jwt_vc = await sign_jwt_with_vault(vc_payload, self.key_name, alg=self.jwt_alg)
        except Exception as exc:
            logger.exception("Vault signing failed")
            raise RuntimeError("Signing VC failed") from exc

        # compute hash of VC for storage/reference
        vc_hash = sha256_hex(jwt_vc.encode("utf-8"))

        # 4) Perform DB operations + callback atomically using a DB transaction:
        #    - create IssuedCredential (pending)
        # Only commit when connector callback succeeds.
        session_factory = getattr(self.postgres, "session_factory", None)
        if session_factory is None:
            # fallback to using service helper methods (best-effort)
            # create audit and issued_credential using service methods if available
            issued = None
            try:
                issued = await self.postgres.create_issued_credential(
                    {
                        "participant_id": str(participant.id),
                        "subject_id": sub,
                        "credential_id": credential_uuid,
                        "credential_hash": vc_hash,
                        "credential_storage_ref": f"connector://{participant.did}/vc/{vc_hash}",
                        "issued_by": KeyVaultSettings.rs_issuer,
                        "issued_at": datetime.now(timezone.utc),
                        "expires_at": None,
                        "status": "pending",
                        "metadata": {"jsonld": jsonld, "ttl_seconds": req.ttl_seconds},
                    }
                )
            except Exception:
                logger.exception("Failed to persist issued credential")
                raise RuntimeError("DB persist failed")

        # 2) store registration request (hashed token) for audit
        token_hash = sha256_hex(req.connector_token.encode("utf-8"))
        try:
            # create_registration_request should be implemented on async_postgres_service
            reg_req = await async_postgres_service.create_registration_request(
                {
                    "participant_id": str(participant.id),
                    "connector_token_hash": token_hash,
                    "token_expires_at": None,
                    "status": "pending",
                    "payload": req.user_claims,
                }
            )
        except AttributeError:
            # service method missing: log and continue but warn
            logger.warning(
                "async_postgres_service.create_registration_request not implemented; skipping DB audit entry"
            )
            reg_req = None
        except Exception:
            logger.exception("Failed to store registration request")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error")

        # 3) Build VC payload
        issued_at = int(__import__("time").time())
        exp = issued_at + (req.ttl_seconds or 3600)
        vc_payload = {
            "iss": KeyVaultSettings.rs_issuer,  # e.g. RS DID or issuer URL from settings
            "sub": req.user_claims.get("sub") or req.user_claims.get("email"),
            "iat": issued_at,
            "nbf": issued_at,
            "exp": exp,
            "vc": {
                "type": ["VerifiableCredential", "UserRegistrationCredential"],
                "credentialSubject": req.user_claims,
            },
            "rcpt": {"participant_did": req.participant_did},
        }

        # 4) Sign VC as a JWT using Vault transit key (key name from settings)
        try:
            signing_key_name = getattr(KeyVaultSettings, "rs_transit_key_name", "rs-signing-key")
            jwt_vc = await sign_jwt_with_vault(
                vc_payload, signing_key_name, alg=getattr(KeyVaultSettings, "rs_jwt_alg", "RS256")
            )
        except Exception:
            logger.exception("Failed to sign VC")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Signing failed")

        # 5) store issued credential metadata (hash + pointer)
        vc_hash = sha256_hex(jwt_vc.encode("utf-8"))
        try:
            issued = await async_postgres_service.create_issued_credential(
                {
                    "participant_id": str(participant.id),
                    "subject_id": vc_payload.get("sub"),
                    "credential_id": None,
                    "credential_hash": vc_hash,
                    "credential_storage_ref": f"connector://{participant.did}/vc/{vc_hash}",
                    "issued_by": KeyVaultSettings.rs_issuer,
                    "expires_at": None,
                    "status": "active",
                    "metadata": {"ttl_seconds": req.ttl_seconds},
                }
            )
        except AttributeError:
            logger.warning("async_postgres_service.create_issued_credential not implemented; skipping DB insert")
            issued = None
        except Exception:
            logger.exception("Failed to persist issued credential metadata")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error")

        # 6) Send VC back to connector callback
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    str(req.connector_callback_url),
                    json={"verifiable_credential": jwt_vc, "connector_token": req.connector_token},
                    headers={"Content-Type": "application/json"},
                )
            if resp.status_code >= 400:
                logger.error(f"Connector callback failed: {resp.status_code} {resp.text}")
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Connector callback failed")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to call connector callback")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

        # 7) respond to caller with metadata


vc_service = VCService()
