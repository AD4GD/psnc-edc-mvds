import logging

from fastapi import HTTPException, status
import httpx
from api.models.dto.responses import UserRegistrationResponse
from api.models.dto.requests import UserRegistrationRequest
from api.core.settings import KeyVaultSettings
from api.services.clients import async_postgres_service
from api.services.helper import sha256_hex, sign_jwt_with_vault
logger = logging.getLogger(__name__)


class UserService:
    """ Service for interacting with User-related operations. """

    def __init__(self):
        pass

    async def create_user(self, req: UserRegistrationRequest) -> dict:
        # TODO check if ok & correct
        # 1) minimal validation: participant must exist
        participant = await async_postgres_service.get_participant_by_did(req.participant_did)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant (connector) not found")

        # 2) store registration request (hashed token) for audit
        token_hash = sha256_hex(req.connector_token.encode("utf-8"))
        try:
            # create_registration_request should be implemented on async_postgres_service
            reg_req = await async_postgres_service.create_registration_request({
                "participant_id": str(participant.id),
                "connector_token_hash": token_hash,
                "token_expires_at": None,
                "status": "pending",
                "payload": req.user_claims,
            })
        except AttributeError:
            # service method missing: log and continue but warn
            logger.warning("async_postgres_service.create_registration_request not implemented; skipping DB audit entry")
            reg_req = None
        except Exception:
            logger.exception("Failed to store registration request")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error")

        # 3) Build VC payload
        issued_at = int(__import__("time").time())
        exp = issued_at + (req.ttl_seconds or 3600)
        vc_payload = {
            "iss": KeyVaultSettings.rs_issuer,               # e.g. RS DID or issuer URL from settings
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
            jwt_vc = await sign_jwt_with_vault(vc_payload, signing_key_name, alg=getattr(KeyVaultSettings, "rs_jwt_alg", "RS256"))
        except Exception as e:
            logger.exception("Failed to sign VC")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Signing failed")

        # 5) store issued credential metadata (hash + pointer)
        vc_hash = sha256_hex(jwt_vc.encode("utf-8"))
        try:
            issued = await async_postgres_service.create_issued_credential({
                "participant_id": str(participant.id),
                "subject_id": vc_payload.get("sub"),
                "credential_id": None,
                "credential_hash": vc_hash,
                "credential_storage_ref": f"connector://{participant.did}/vc/{vc_hash}",
                "issued_by": KeyVaultSettings.rs_issuer,
                "expires_at": None,
                "status": "active",
                "metadata": {"ttl_seconds": req.ttl_seconds},
            })
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
        return UserRegistrationResponse(
            credential_id=(issued.id if issued is not None else vc_hash),
            credential_hash=vc_hash,
            issued_at=str(issued_at),
            issued_to=str(vc_payload.get("sub")),
            storage_ref=(issued.credential_storage_ref if issued is not None else f"connector://{participant.did}/vc/{vc_hash}"),
        )


user_service = UserService()
