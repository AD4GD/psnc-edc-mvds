import asyncio
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings, ProjectSettings
from api.exceptions.registration_service_exceptions import RecordAlreadyExistsException, RecordNotFoundException
from api.models.dto.local import KeyDataType, KeyInfo, KeyTypeEnum, PublicKeyType
from api.services.helper import b64url
from api.templates.dict_templates import DIDK8sDict, VerificationMethodDict
from api.templates.keys import did_k8s_template, verification_method_template
from api.templates.template_filler import render_json_template_string
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from fastapi import status
from fastapi.responses import Response
from hvac import Client, exceptions
from hvac.api.secrets_engines.transit import Transit

logger = setup_logging()


class VaultService:
    """
    Service for secure cryptographic operations using HashiCorp Vault.

    Supports:
    - Asymmetric key management (RSA, ECDSA, Ed25519)
    - Digital signatures for Verifiable Credentials (VC)
    - Public key storage and retrieval
    - Key rotation and versioning
    """

    def __init__(self):
        """Initialize Vault client with authentication check."""
        self.client = Client(url=KeyVaultSettings.vault_url, token=KeyVaultSettings.vault_token)
        self.transit: Transit = self.client.secrets.transit

        if not self.client.is_authenticated():
            raise RuntimeError("Vault authentication failed")

        # Mount points
        self.kv_mount = getattr(KeyVaultSettings, "vault_kv_mount", "secret")
        self.transit_mount = getattr(KeyVaultSettings, "vault_transit_mount", "transit")
        self.key_name = getattr(KeyVaultSettings, "key_name", "key_name")
        self.issuer_did = getattr(ProjectSettings, "issuer_did", "did:web:issuer")

        logger.info(f"VaultService initialized: KV={self.kv_mount}, Transit={self.transit_mount}")

    # ==================== HEALTH CHECK ====================

    def health(self) -> bool:
        """Check Vault server health and initialization status."""
        health: dict = self.client.sys.read_health_status(method="GET")
        return health.get("initialized", False) and not health.get("sealed", True)

    # ==================== KEY MANAGEMENT ====================

    def create_signing_key(
        self,
        key_name: str,
        key_type: KeyTypeEnum = KeyTypeEnum.ED25519,
        mount_point: Optional[str] = None,
        auto_rotate_days: Optional[int] = 30,
    ) -> Dict[str, Any]:
        """
        Create a signing key in Transit engine.

        Args:
            key_name: Unique identifier for the key (e.g., "issuer-key-2024")
            key_type: Type of asymmetric key (ed25519 recommended for VC)
            auto_rotate_days: Auto-rotation days that are transformed into hours

        Returns:
            API response dict
        """
        try:
            params = {
                "name": key_name,
                "key_type": key_type,
                "mount_point": mount_point if mount_point else self.transit_mount,
                "auto_rotate_period": f"{auto_rotate_days}d",
            }

            response = self.transit.create_key(**params)
            logger.info(f"Created signing key '{key_name}' (type={key_type})")
            return response
        except exceptions.InvalidRequest as e:
            if "already exists" in str(e).lower() or "existing key" in str(e).lower():
                logger.warning(f"Key '{key_name}' already exists")
                return {"warning": "key_already_exists"}
            raise RecordAlreadyExistsException(message=f"Key '{key_name}' already exists")

    def get_public_key(self, key_name: str, version: Optional[int] = None) -> PublicKeyType:
        """
        Retrieve public key from Transit key.
        Args:
            key_name: Name of the Transit key
            version: Specific version (None = latest)
        Returns:
            Dict of type KeyInfo
        """
        try:
            response = self.transit.read_key(name=self.key_name, mount_point=self.transit_mount)
            key_data: KeyDataType = response["data"]
            keys = key_data.get("keys", {})

            if version:
                version_str = str(version)
                if version_str not in keys:
                    raise RecordNotFoundException(
                        message="Key version not found in Vault", record_id=key_name, record_type="key version", status_code=204
                    )
                key_info: KeyInfo = keys[version_str]
            else:
                # Get latest version
                latest_version = str(key_data.get("latest_version", 1))
                key_info: KeyInfo = keys[latest_version]

            return {
                "public_key": key_info.get("public_key"),
                "key_type": key_data.get("type"),
                "name": key_data.get("name"),
                "version": version or key_data.get("latest_version"),
                "creation_time": key_info.get("creation_time"),
                "expiration_time": (
                    datetime.fromisoformat(key_info.get("creation_time")) + timedelta(seconds=key_data.get("auto_rotate_period"))
                ).isoformat(),
                "supports_signing": key_data.get("supports_signing"),
            }
        except exceptions.InvalidPath as e:
            logger.error(f"Failed to get public key for '{key_name}': {e}")
            raise RecordNotFoundException(message="Key not found in Vault", record_id=key_name, record_type="key", status_code=204)
        except Exception as e:  # pylint: disable=W0718
            logger.error(f"Failed to get public key for '{key_name}': {e}")
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    def get_public_key_pem(self, key_name: str, version: Optional[int] = None) -> str:
        """
        Retrieve public key from Vault and convert to PEM format.

        Args:
            key_name: Name of the Transit key
            version: Specific version (None = latest)

        Returns:
            Public key in PEM format (string)
        """
        # Pobierz klucz z Vault (base64)
        key_info = self.get_public_key(key_name, version)
        public_key_b64 = key_info["public_key"]

        try:
            # Dekoduj Base64 -> surowe bajty (32 bajty dla Ed25519)
            public_key_bytes = base64.b64decode(public_key_b64)

            # Utwórz obiekt klucza publicznego Ed25519
            public_key_obj = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

            # Konwertuj do formatu PEM
            pem = public_key_obj.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

            return pem.decode("utf-8")

        except Exception as e:
            logger.error(f"Failed to convert public key to PEM: {e}")
            raise

    def list_keys(self) -> list[str]:
        """List all Transit keys."""
        response: Dict = self.transit.list_keys(mount_point=self.transit_mount)
        return response.get("data", {}).get("keys", [])

    def prepare_did_document(self):
        """
        Prepare a DID Document using the public key from Vault.
        Returns:
            DID Document dict
        """
        key_info = self.get_public_key(self.key_name)
        public_key_pem = b64url(base64.b64decode(key_info["public_key"]))
        version = key_info["version"]

        verification_method = render_json_template_string(
            verification_method_template,
            VerificationMethodDict(
                issuer=ProjectSettings.issuer_did, issuer_key_id=f"{ProjectSettings.issuer_did}#key-{version}", key_hash=public_key_pem
            ),
        )
        did_k8s = render_json_template_string(
            did_k8s_template,
            DIDK8sDict(
                issuer=ProjectSettings.issuer_did,
                list_of_verification_methods=[verification_method],
                list_of_key_ids=[f"key-{version}"],
            ),
        )
        return did_k8s

    def rotate_key(self, key_name: str) -> Dict[str, Any]:
        """
        Manually rotate a Transit key (creates new version).

        Args:
            key_name: Name of key to rotate

        Returns:
            API response
        """
        try:
            response = self.transit.rotate_key(name=key_name, mount_point=self.transit_mount)
            logger.info(f"Rotated key '{key_name}'")
            return response
        except Exception as e:
            logger.error(f"Failed to rotate key '{key_name}': {e}")
            raise

    def delete_key(self, key_name: str) -> Dict[str, Any]:
        """
        Delete a Transit key (requires deletion_allowed=true on key).

        Args:
            key_name: Name of key to delete

        Returns:
            API response
        """
        try:
            # First, update key config to allow deletion
            self.transit.update_key_configuration(name=key_name, deletion_allowed=True, mount_point=self.transit_mount)
            # Then delete
            response = self.transit.delete_key(name=key_name, mount_point=self.transit_mount)
            logger.info(f"Deleted key '{key_name}'")
            return response
        except Exception as e:
            logger.error(f"Failed to delete key '{key_name}': {e}")
            raise

    # ==================== SIGNING & VERIFICATION ====================

    def sign_data(
        self,
        key_name: str,
        data: bytes,
        hash_algorithm: Optional[str] = None,
        prehashed: bool = False,
        key_version: Optional[int] = None,
    ) -> str:
        """
        Sign arbitrary data using Transit key.

        Args:
            key_name: Name of signing key
            data: Raw data to sign
            hash_algorithm: Hash algorithm (sha2-256, sha2-384, sha2-512, none for ed25519)
            prehashed: Whether data is already hashed
            key_version: Specific key version to use (None = latest)

        Returns:
            Vault signature string (format: "vault:v{version}:{base64_signature}")

        Example:
            signature = vault.sign_data("issuer-key", b"credential_data")
            # Returns: "vault:v1:MEUCIQDx..."
        """
        try:
            input_b64 = base64.b64encode(data).decode("utf-8")

            params = {
                "name": key_name,
                "hash_input": input_b64,
                "mount_point": self.transit_mount,
            }

            if hash_algorithm:
                params["hash_algorithm"] = hash_algorithm

            if prehashed:
                params["prehashed"] = True

            if key_version:
                params["key_version"] = key_version

            response = self.transit.sign_data(**params)
            signature = response["data"]["signature"]

            logger.debug(f"Signed data with key '{key_name}'")
            return signature

        except Exception as e:
            logger.error(f"Failed to sign data with '{key_name}': {e}")
            raise

    async def make_jwt(self, payload: Dict, key_name: str, verification_method: str) -> str:
        """
        Creates a signed JWT (JWS) using Vault for signing.
        Handles Vault's specific response format and ensures URL-safe Base64 encoding.
        """
        # 1. Prepare Header
        # EdDSA is standard for Ed25519 keys. If using RSA, change to RS256.
        header = {"alg": "EdDSA", "typ": "JWT", "kid": verification_method}

        header_b64 = b64url(json.dumps(header, separators=(",", ":")).encode())
        payload_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode())
        signing_input = f"{header_b64}.{payload_b64}".encode()

        # vault_response = self.sign_data(key_name, signing_input)
        signature = await asyncio.to_thread(
            self.sign_data,
            key_name,
            signing_input
            # hash_algorithm=HashAlgorithmEnum.SHA2_256 # Uncomment if using RSA/EC keys
        )

        # 3. Parse Vault Response (format: "vault:v1:base64_signature")
        try:
            # Extract the base64 part after the last colon
            print(signature)
            sig_base64_std = signature.split(":")[-1]
        except AttributeError:
            # Fallback if Vault returns raw bytes or unexpected format
            sig_base64_std = signature
        # 4. Convert Standard Base64 (Vault) -> Raw Bytes -> URL-Safe Base64 (JWT)
        sig_b64url = b64url(base64.b64decode(sig_base64_std))
        # sig_b64url = b64url(sig_bytes)
        print(sig_base64_std)
        print(sig_b64url)

        return f"{header_b64}.{payload_b64}.{sig_b64url}"

    def verify_signature(self, key_name: str, data: bytes, signature: str, hash_algorithm: Optional[str] = None, prehashed: bool = False) -> bool:
        """
        Verify signature created by Transit key.

        Args:
            key_name: Name of signing key
            data: Original data that was signed
            signature: Vault signature string (from sign_data)
            hash_algorithm: Hash algorithm (must match signing)
            prehashed: Whether data is already hashed

        Returns:
            True if signature is valid, False otherwise
        """
        input_b64 = base64.b64encode(data).decode("utf-8")

        params = {
            "name": key_name,
            "hash_input": input_b64,
            "signature": signature,
            "mount_point": self.transit_mount,
        }

        if hash_algorithm:
            params["hash_algorithm"] = hash_algorithm

        if prehashed:
            params["prehashed"] = True

        response = self.transit.verify_signed_data(**params)
        is_valid = response.get("data", {}).get("valid", False)

        logger.debug(f"Signature verification for '{key_name}': {is_valid}")
        return is_valid

    # ==================== VERIFIABLE CREDENTIALS SUPPORT ====================

    def sign_verifiable_credential(self, key_name: str, credential: Dict[str, Any], proof_purpose: str = "assertionMethod") -> Dict[str, Any]:
        """
        Sign a Verifiable Credential with proper proof format.

        Args:
            key_name: Transit key name (issuer's signing key)
            credential: VC document (dict without proof)
            proof_purpose: Purpose of proof (assertionMethod, authentication, etc.)

        Returns:
            Complete VC with embedded proof

        Example:
            vc = {
                "@context": [...],
                "type": ["VerifiableCredential"],
                "issuer": "did:example:123",
                "issuanceDate": "2024-01-01T00:00:00Z",
                "credentialSubject": {...}
            }
            signed_vc = vault.sign_verifiable_credential("issuer-key", vc)
        """
        try:
            # Get public key info for proof metadata
            key_info = self.get_public_key(key_name)

            # Create canonical representation for signing
            # (In production, use proper JSON-LD canonicalization)
            canonical = json.dumps(credential, sort_keys=True, separators=(",", ":"))
            credential_bytes = canonical.encode("utf-8")

            # Sign the credential
            signature = self.sign_data(key_name, credential_bytes)

            # Extract just the signature part (remove "vault:v1:" prefix)
            # Format: vault:v{version}:{signature}
            sig_parts = signature.split(":")
            vault_signature = sig_parts[2] if len(sig_parts) == 3 else signature

            # Create proof object
            proof = {
                "type": "Ed25519Signature2020",  # Adjust based on key_type
                "created": datetime.now(timezone.utc).isoformat() + "Z",
                "verificationMethod": f"#key-{key_info['version']}",
                "proofPurpose": proof_purpose,
                "proofValue": vault_signature,
                # Store full vault signature for internal verification
                "_vaultSignature": signature,
            }

            # Add proof to credential
            signed_credential = credential.copy()
            signed_credential["proof"] = proof

            logger.info(f"Signed VC with key '{key_name}'")
            return signed_credential

        except Exception as e:
            logger.error(f"Failed to sign VC: {e}")
            raise

    def verify_verifiable_credential(self, key_name: str, signed_credential: Dict[str, Any]) -> bool:
        """
        Verify a signed Verifiable Credential.

        Args:
            key_name: Transit key name used for signing
            signed_credential: Complete VC with proof

        Returns:
            True if signature is valid
        """
        # Extract proof
        proof = signed_credential.get("proof")
        if not proof:
            logger.error("No proof found in credential")
            return False

        # Get vault signature
        vault_signature = proof.get("_vaultSignature")
        if not vault_signature:
            logger.error("No Vault signature in proof")
            return False

        # Remove proof to get original credential
        credential = {k: v for k, v in signed_credential.items() if k != "proof"}

        # Create canonical representation
        canonical = json.dumps(credential, sort_keys=True, separators=(",", ":"))
        credential_bytes = canonical.encode("utf-8")

        # Verify signature
        is_valid = self.verify_signature(key_name, credential_bytes, vault_signature)

        logger.info(f"VC verification result: {is_valid}")
        return is_valid

    # ==================== PUBLIC KEY STORAGE (KV) ====================

    def store_public_key_metadata(self, key_id: str, public_key_pem: str, meta: Optional[Dict[str, Any]] = None) -> str:
        """
        Store public key and metadata in KV v2.

        Args:
            key_id: Unique identifier (e.g., DID, user_id)
            public_key_pem: Public key in PEM format
            meta Additional metadata (owner, created_at, purpose, etc.)

        Returns:
            Storage path reference
        """
        path = f"public-keys/{key_id}"

        secret_data = {
            "public_key": public_key_pem,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if meta:
            secret_data.update({"meta": meta})

        try:
            self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=secret_data, mount_point=self.kv_mount)
            logger.info(f"Stored public key for '{key_id}'")
            return f"{self.kv_mount}/data/{path}"
        except Exception as e:
            logger.error(f"Failed to store public key: {e}")
            raise

    def read_public_key_metadata(self, key_id: str) -> Optional[Dict[str, Any]]:
        """
        Read public key and metadata from KV v2.

        Args:
            key_id: Key identifier

        Returns:
            Dict with public_key and metadata, or None if not found
        """
        path = f"public-keys/{key_id}"

        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=self.kv_mount, raise_on_deleted_version=True)
            return response["data"]["data"]
        except exceptions.InvalidPath:
            logger.warning(f"Public key not found: '{key_id}'")
            return None


# Singleton instance
vault_service = VaultService()
