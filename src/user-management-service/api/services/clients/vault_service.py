import base64
import json
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings
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

    # Supported key types for different use cases
    KEY_TYPES = {
        "ed25519": "ed25519",  # Fast signing, small signatures (VC preferred)
        "ecdsa-p256": "ecdsa-p256",  # NIST P-256, widely supported
        "ecdsa-p384": "ecdsa-p384",  # Higher security NIST curve
        "rsa-2048": "rsa-2048",  # Legacy compatibility
        "rsa-3072": "rsa-3072",  # Balanced RSA
        "rsa-4096": "rsa-4096",  # High security RSA
    }

    def __init__(self):
        """Initialize Vault client with authentication check."""
        return
    
        self.client = Client(url=KeyVaultSettings.vault_url, token=KeyVaultSettings.vault_token)
        self.transit: Transit = self.client.secrets.transit

        if not self.client.is_authenticated():
            raise RuntimeError("Vault authentication failed")

        # Mount points
        self.kv_mount = getattr(KeyVaultSettings, "vault_kv_mount", "secret")
        self.transit_mount = getattr(KeyVaultSettings, "vault_transit_mount", "transit")

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
        key_type: Literal[
            "ed25519",
            "ecdsa-p256",
            "ecdsa-p384",
            "rsa-2048",
            "rsa-3072",
            "rsa-4096",
            "aes256-gcm96",
            "chacha20-poly1305",
        ] = "ed25519",
        derived: bool = False,
        exportable: bool = False,
        allow_plaintext_backup: bool = False,
        auto_rotate_period: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a signing key in Transit engine.

        Args:
            key_name: Unique identifier for the key (e.g., "issuer-key-2024")
            key_type: Type of asymmetric key (ed25519 recommended for VC)
            derived: Boolean - used with "chacha20-poly1305" key - allows for encryption with context
            exportable: Allow key export (WARNING: security risk)
            allow_plaintext_backup: Allow plaintext backup (WARNING: security risk)
            auto_rotate_period: Auto-rotation period (e.g., "720h" for 30 days)

        Returns:
            API response dict

        Raises:
            Exception if key creation fails
        """
        try:
            response = self.client.secrets.transit.create_key(
                name=key_name,
                convergent_encryption=False,
                derived=derived,
                # exportable=exportable,
                # allow_plaintext_backup=allow_plaintext_backup,
                key_type=key_type,
                mount_point=self.transit_mount,
                auto_rotate_period=auto_rotate_period,
            )
            logger.info(f"Created signing key '{key_name}' (type={key_type})")
            return response
        except exceptions.InvalidRequest as e:
            # Key might already exist
            if "already exists" in str(e).lower() or "existing key" in str(e).lower():
                logger.warning(f"Key '{key_name}' already exists")
                return {"warning": "key_already_exists"}
            raise

    def get_public_key(self, key_name: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve public key from Transit key.

        Args:
            key_name: Name of the Transit key
            version: Specific version (None = latest)

        Returns:
            Dict with 'public_key' (PEM), 'key_type', 'versions', etc.
        """
        try:
            response = self.client.secrets.transit.read_key(name=key_name, mount_point=self.transit_mount)

            key_data = response["data"]
            keys = key_data.get("keys", {})

            if version:
                version_str = str(version)
                if version_str not in keys:
                    raise ValueError(f"Version {version} not found for key '{key_name}'")
                key_info = keys[version_str]
            else:
                # Get latest version
                latest_version = str(key_data.get("latest_version", 1))
                key_info = keys[latest_version]

            return {
                "public_key": key_info.get("public_key"),
                "key_type": key_data.get("type"),
                "name": key_data.get("name"),
                "version": version or key_data.get("latest_version"),
                "creation_time": key_info.get("creation_time"),
                "exportable": key_data.get("exportable"),
                "supports_signing": key_data.get("supports_signing"),
            }
        except Exception as e:
            logger.error(f"Failed to get public key for '{key_name}': {e}")
            raise

    def list_keys(self) -> list[str]:
        """List all Transit keys."""
        response: Dict = self.client.secrets.transit.list_keys(mount_point=self.transit_mount)
        return response.get("data", {}).get("keys", [])

    def rotate_key(self, key_name: str) -> Dict[str, Any]:
        """
        Manually rotate a Transit key (creates new version).

        Args:
            key_name: Name of key to rotate

        Returns:
            API response
        """
        try:
            response = self.client.secrets.transit.rotate_key(name=key_name, mount_point=self.transit_mount)
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
            self.client.secrets.transit.update_key_configuration(name=key_name, deletion_allowed=True, mount_point=self.transit_mount)
            # Then delete
            response = self.client.secrets.transit.delete_key(name=key_name, mount_point=self.transit_mount)
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

            response = self.client.secrets.transit.sign_data(**params)
            signature = response["data"]["signature"]

            logger.debug(f"Signed data with key '{key_name}'")
            return signature

        except Exception as e:
            logger.error(f"Failed to sign data with '{key_name}': {e}")
            raise

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

        response = self.client.secrets.transit.verify_signed_data(**params)
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

    # ==================== ENCRYPTION/DECRYPTION ====================

    def encrypt_data(self, key_name: str, plaintext: bytes, context: Optional[str] = None, key_version: Optional[int] = None) -> str:
        """
        Encrypt data using Transit key.

        Args:
            key_name: Transit key name (must support encryption)
            plaintext: Data to encrypt
            context: Additional authenticated data (base64)
            key_version: Specific key version

        Returns:
            Vault ciphertext (format: "vault:v{version}:{ciphertext}")
        """
        try:
            plaintext_b64 = base64.b64encode(plaintext).decode("utf-8")

            params = {
                "name": key_name,
                "plaintext": plaintext_b64,
                "mount_point": self.transit_mount,
            }

            if context:
                context_b64 = base64.b64encode(context.encode("utf-8")).decode("utf-8")
                params["context"] = context_b64
            if key_version:
                params["key_version"] = key_version

            response = self.client.secrets.transit.encrypt_data(**params)
            return response["data"]["ciphertext"]

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt_data(self, key_name: str, ciphertext: str, context: Optional[str] = None) -> bytes:
        """
        Decrypt Vault ciphertext.

        Args:
            key_name: Transit key name
            ciphertext: Vault ciphertext string
            context: Additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext bytes
        """
        try:
            params = {
                "name": key_name,
                "ciphertext": ciphertext,
                "mount_point": self.transit_mount,
            }

            if context:
                context_b64 = base64.b64encode(context.encode("utf-8")).decode("utf-8")
                params["context"] = context_b64

            response = self.client.secrets.transit.decrypt_data(**params)
            plaintext_b64 = response["data"]["plaintext"]
            return base64.b64decode(plaintext_b64)

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    # ==================== GENERIC KV OPERATIONS ====================

    def store_secret(self, path: str, secret: Dict[str, Any]) -> str:
        """Store arbitrary secret in KV v2."""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=secret, mount_point=self.kv_mount)
            logger.info(f"Stored secret at '{path}'")
            return f"{self.kv_mount}/data/{path}"
        except Exception as e:
            logger.error(f"Failed to store secret: {e}")
            raise

    def read_secret(self, path: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Read secret from KV v2."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path, version=version, raise_on_deleted_version=True, mount_point=self.kv_mount
            )
            return response["data"]["data"]
        except exceptions.InvalidPath:
            logger.warning(f"Secret not found: '{path}'")
            return None

    def delete_secret(self, path: str, versions: Optional[list[int]] = None) -> Dict[str, Any]:
        """
        Delete secret versions from KV v2.

        Args:
            path: Secret path
            versions: Specific versions to delete (None = mark latest as deleted)
        """
        if versions:
            response = self.client.secrets.kv.v2.delete_secret_versions(path=path, versions=versions, mount_point=self.kv_mount)
        else:
            response = self.client.secrets.kv.v2.delete_latest_version_of_secret(path=path, mount_point=self.kv_mount)
        logger.info(f"Deleted secret at '{path}'")
        return response


# Singleton instance
vault_service = VaultService()
