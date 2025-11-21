from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict
from uuid import UUID
from enum import StrEnum
from pydantic import AnyHttpUrl, BaseModel, Field



class KeyTypeEnum(StrEnum):
    ED25519 = "ed25519"  # Fast signing, small signatures (VC preferred)
    ECDA_P256 = "ecdsa-p256"  # NIST P-256, widely supported
    ECDA_P384 = "ecdsa-p384"  # Higher security NIST curve
    RSA_2048 = "rsa-2048"  # Legacy compatibility
    RSA_3072 = "rsa-3072"  # Balanced RSA
    RSA_4096 = "rsa-4096"  # High security RSA
    AES256_GCM96 = "aes256-gcm96"  # Encryption key type


class KeyInfo(TypedDict):
    certificate_chain: str
    creation_time: datetime
    name: str
    public_key: str


class KeyDataType(TypedDict):
    allow_plaintext_backup: bool
    auto_rotate_period: int # seconds
    deletion_allowed: bool
    derived: bool
    exportable: bool
    imported_key: bool
    keys: Dict[str, KeyInfo]
    latest_version: int
    min_available_version: int
    min_decryption_version: int
    min_encryption_version: int
    name: str
    supports_decryption: bool
    supports_derivation: bool
    supports_encryption: bool
    supports_signing: bool
    type: KeyTypeEnum

class PublicKeyType(BaseModel):
    public_key: str
    key_type: KeyTypeEnum
    name: str
    version: int
    creation_time: datetime
    expiration_time: datetime
    supports_signing: bool

# ---------------------------
# Shared / Base schema
# ---------------------------
class TimestampedModel(BaseModel):
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")



# ---------------------------
# Location schemas
# ---------------------------
class LocationCreate(BaseModel):
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    street: Optional[str] = Field(None, max_length=200)
    building_number: Optional[str] = Field(None, max_length=20)


class LocationUpdate(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    street: Optional[str] = None
    building_number: Optional[str] = None


class LocationInDB(LocationCreate, TimestampedModel):
    id: UUID = Field(...)


class LocationResponse(LocationInDB):
    pass


# ---------------------------
# Participant schemas
# ---------------------------
class ParticipantCreate(BaseModel):
    did: str = Field(..., description="Decentralized identifier of participant")
    protocol_url: AnyHttpUrl = Field(..., description="URL to registration/protocol endpoint")
    location_id: Optional[UUID] = Field(None, description="FK to location")
    error_detail: Optional[str] = Field(None)


class ParticipantUpdate(BaseModel):
    protocol_url: Optional[AnyHttpUrl] = None
    location_id: Optional[UUID] = None
    error_detail: Optional[str] = None


class ParticipantInDB(ParticipantCreate, TimestampedModel):
    id: UUID = Field(...)


class ParticipantResponse(ParticipantInDB):
    pass


# ---------------------------
# Participant key / JWKS
# ---------------------------
class ParticipantKeyCreate(BaseModel):
    key_type: Optional[str] = Field("jwks", description="Type of key (jwks, signing, ...)")
    public_key: str = Field(..., description="Public key material (PEM or JWK JSON)")
    jwks_uri: Optional[AnyHttpUrl] = Field(None)


class ParticipantKeyInDB(ParticipantKeyCreate, TimestampedModel):
    id: UUID = Field(...)
    participant_id: UUID = Field(...)


class ParticipantKeyResponse(ParticipantKeyInDB):
    pass


# ---------------------------
# Registration request schemas
# ---------------------------
class RegistrationRequestCreate(BaseModel):
    participant_id: Optional[UUID] = Field(None, description="Associated participant (if known)")
    connector_token: str = Field(..., description="Token provided by connector (store hashed/encrypted)")
    token_expires_at: Optional[datetime] = Field(None)
    payload: Optional[Dict[str, Any]] = Field(None, description="Raw request payload/metadata")


class RegistrationRequestInDB(RegistrationRequestCreate, TimestampedModel):
    id: UUID = Field(...)
    status: str = Field(..., description="pending/accepted/rejected/expired")


class RegistrationRequestResponse(RegistrationRequestInDB):
    pass


# ---------------------------
# Issued credential schemas
# ---------------------------
class IssuedCredentialCreate(BaseModel):
    participant_id: UUID = Field(..., description="Owner participant")
    subject_id: str = Field(..., description="Subject identifier (user DID or connector user id)")
    credential_id: Optional[str] = Field(None, description="Credential id inside VC")
    credential_hash: Optional[str] = Field(None, description="Hash of stored VC")
    credential_storage_ref: Optional[str] = Field(None, description="Pointer where VC is stored (e.g. connector://...)")
    issued_by: Optional[str] = Field(None, description="Issuer id")
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class IssuedCredentialInDB(IssuedCredentialCreate, TimestampedModel):
    id: UUID = Field(...)
    status: str = Field("active", description="active/revoked/expired")


class IssuedCredentialResponse(IssuedCredentialInDB):
    pass


# ---------------------------
# User reference (mapping)
# ---------------------------
class UserReferenceCreate(BaseModel):
    participant_id: UUID = Field(...)
    connector_user_id: str = Field(..., description="User id in connector Keycloak")
    connector_endpoint: AnyHttpUrl = Field(...)


class UserReferenceInDB(UserReferenceCreate, TimestampedModel):
    id: UUID = Field(...)


class UserReferenceResponse(UserReferenceInDB):
    pass


# ---------------------------
# API list / pagination helpers
# ---------------------------
class PageMeta(BaseModel):
    limit: int = Field(10)
    offset: int = Field(0)
    total: Optional[int] = Field(None)


class ParticipantListResponse(BaseModel):
    items: List[ParticipantResponse]
    meta: PageMeta


class LocationListResponse(BaseModel):
    items: List[LocationResponse]
    meta: PageMeta
