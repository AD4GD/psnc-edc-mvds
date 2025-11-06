from typing import TypedDict, Dict, List


class JsonLdDict(TypedDict):
    credential_id : str
    issuer : str
    issuance_date_iso : str
    expiration_date_iso : str
    user_did : str
    contract_version : str
    processing_level : str
    claims : List
    alumniOf : Dict | None


class VCDict(TypedDict):
    issuer : str
    user_did : str
    vc : JsonLdDict
    issued_at : str
    expires_at : str
    metadata_vc : str | Dict | None
