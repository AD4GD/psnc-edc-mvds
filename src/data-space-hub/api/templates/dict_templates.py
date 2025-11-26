from typing import Any, Dict, List, Optional, TypedDict

from api.models.dto.local import CredentialFormatEnum


class JsonLdDict(TypedDict):
    alumniOf: Optional[Dict | None] = None
    claims: List[Dict[str, Any]]
    context_for: Dict[str, Any]
    contract_version: str
    credential_id: str
    credential_schema: Dict[str, Any] | None = None
    credential_status: Dict[str, Any] | None = None
    description: str = ""
    issuer: str
    issuance_date_iso: str
    expiration_date_iso: str
    list_of_credential_types: List[str]
    name: str = ""
    processing_level: str
    user_did: str


class VCDict(TypedDict):
    issuer: str
    user_did: str
    vc: JsonLdDict
    issued_at: int
    expires_at: int
    metadata_vc: str | Dict | None


class FullCredentialDict(TypedDict):
    credential_id: str
    credential_ld: Dict[str, Any]
    creation_timestamp: int
    issuer_did: str
    issuance_policy: Dict[str, Any] | None = None
    raw_vc_jwt: str
    reissuance_policy: Dict[str, Any] | None = None
    state: int = 500
    user_did: str
    vc_format: CredentialFormatEnum


class ProofDict(TypedDict):
    key_created_date_iso: str
    raw_vc_jwt: str
    verification_method: str


class VerificationMethodDict(TypedDict):
    issuer: str
    issuer_key_id: str  # <issuer>#<key-id>
    key_hash: str


class DIDK8sDict(TypedDict):
    issuer: str
    list_of_verification_methods: List[str]
    list_of_key_ids: List[str]
