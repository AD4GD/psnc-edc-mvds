from typing import Dict, List, TypedDict, Optional


class JsonLdDict(TypedDict):
    credential_id: str
    issuer: str
    issuance_date_iso: str
    expiration_date_iso: str
    user_did: str
    contract_version: str
    processing_level: str
    claims: List
    alumniOf: Optional[Dict | None] = None


class VCDict(TypedDict):
    issuer: str
    user_did: str
    vc: JsonLdDict
    issued_at: str
    expires_at: str
    metadata_vc: str | Dict | None


class VerificationMethodDict(TypedDict):
    issuer: str
    issuer_key_id: str # <issuer>#<key-id>
    key_hash: str


class DIDK8sDict(TypedDict):
    issuer: str
    list_of_verification_methods : List[str]
    list_of_key_ids : List[str]
