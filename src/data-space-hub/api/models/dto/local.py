from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Dict, TypedDict

from pydantic import BaseModel


class KeyTypeEnum(StrEnum):
    ED25519 = "ed25519"  # Fast signing, small signatures (VC preferred)
    ECDA_P256 = "ecdsa-p256"  # NIST P-256, widely supported
    ECDA_P384 = "ecdsa-p384"  # Higher security NIST curve
    RSA_2048 = "rsa-2048"  # Legacy compatibility
    RSA_3072 = "rsa-3072"  # Balanced RSA
    RSA_4096 = "rsa-4096"  # High security RSA
    AES256_GCM96 = "aes256-gcm96"  # Encryption key type


class HashAlgorithmEnum(StrEnum):
    SHA2_256 = "sha2-256"
    SHA2_384 = "sha2-384"
    SHA2_512 = "sha2-512"
    NONE = "none"  # for ed25519


class CredentialFormatEnum(StrEnum):
    VC1_0_LD = "VC1_0_LD"
    VC1_0_JWT = "VC1_0_JWT"
    VC2_0_JOSE = "VC2_0_JOSE"


class KeyInfo(TypedDict):
    certificate_chain: str
    creation_time: datetime
    name: str
    public_key: str


class KeyDataType(TypedDict):
    allow_plaintext_backup: bool
    auto_rotate_period: int  # seconds
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
