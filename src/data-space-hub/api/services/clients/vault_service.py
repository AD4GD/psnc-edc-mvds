import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings, ProjectSettings
from api.exceptions.registration_service_exceptions import RecordAlreadyExistsException, RecordNotFoundException
from api.models.dto.local import KeyDataType, KeyInfo, KeyTypeEnum, PublicKeyType
from api.templates.dict_templates import DIDK8sDict, VerificationMethodDict
from api.templates.keys import did_k8s_template, verification_method_template
from api.templates.template_filler import render_json_template_string
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
        public_key_pem = key_info["public_key"]
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

            response = self.transit.encrypt_data(**params)
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

            response = self.transit.decrypt_data(**params)
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
#     def get_public_key(self, key_name: str) -> Dict[str, Any]:
#         response = self.transit.read_key(name=key_name, mount_point=self.transit_mount)
#         key_data = response["data"]
#         keys = key_data.get("keys", {})
#         latest_version = str(key_data.get("latest_version", 1))
#         key_info = keys[latest_version]
#         return {
#             "public_key": key_info.get("public_key"),
#             "key_type": key_data.get("type"),
#             "name": key_data.get("name"),
#             "version": key_data.get("latest_version"),
#             "creation_time": key_info.get("creation_time")
#         }

#     def list_keys(self) -> list[str]:
#         response: Dict = self.transit.list_keys(mount_point=self.transit_mount)
#         return response.get("data", {}).get("keys", [])

#     def rotate_key(self, key_name: str) -> Dict[str, Any]:
#         return self.transit.rotate_key(name=key_name, mount_point=self.transit_mount)

#     def delete_key(self, key_name: str) -> Dict[str, Any]:
#         self.transit.update_key_configuration(
#             name=key_name, deletion_allowed=True, mount_point=self.transit_mount)
#         return self.transit.delete_key(name=key_name, mount_point=self.transit_mount)

#     # Signing & Verification
#     def sign_data(self, key_name: str, data: bytes) -> str:
#         input_b64 = base64.b64encode(data).decode("utf-8")
#         response = self.transit.sign_data(
#             name=key_name,
#             hash_input=input_b64,
#             mount_point=self.transit_mount
#         )
#         return response["data"]["signature"]

#     def verify_signature(self, key_name: str, data: bytes, signature: str) -> bool:
#         input_b64 = base64.b64encode(data).decode("utf-8")
#         response = self.transit.verify_signed_data(
#             name=key_name,
#             hash_input=input_b64,
#             signature=signature,
#             mount_point=self.transit_mount
#         )
#         return response.get("data", {}).get("valid", False)

#     # Signing VC as JWT
#     def sign_vc_as_jwt(
#         self,
#         key_name: str,
#         credential: Dict[str, Any],
#         issuer_did: str,
#         subject_did: Optional[str] = None,
#         ttl_seconds: int = 3600
#     ) -> str:
#         import time
#         now = int(time.time())
#         claims = {
#             "iss": issuer_did,
#             "iat": now,
#             "exp": now + ttl_seconds,
#             "vc": credential,
#         }
#         if subject_did:
#             claims["sub"] = subject_did

#         headers = {
#             "typ": "JWT",
#             "alg": "EdDSA",
#             "kid": f"{issuer_did}#{key_name}",
#         }
#         header_json = json.dumps(headers, separators=(",", ":"))
#         payload_json = json.dumps(claims, separators=(",", ":"))
#         header_b64 = base64.urlsafe_b64encode(header_json.encode()).rstrip(b"=").decode()
#         payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).rstrip(b"=").decode()
#         signing_input = f"{header_b64}.{payload_b64}".encode()
#         vault_signature = self.sign_data(key_name, signing_input)
#         raw_sig = vault_signature.split(":")[-1]
#         sig_bytes = base64.b64decode(raw_sig)
#         sig_b64 = base64.urlsafe_b64encode(sig_bytes).rstrip(b"=").decode()
#         return f"{header_b64}.{payload_b64}.{sig_b64}"

#     def verify_vc_jwt(self, key_name: str, jwt_token: str) -> Tuple[bool, Dict[str, Any]]:
#         parts = jwt_token.split(".")
#         if len(parts) != 3:
#             return False, {}
#         header_b64, payload_b64, sig_b64 = parts
#         signing_input = f"{header_b64}.{payload_b64}".encode()
#         sig_bytes = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))
#         sig_b64_std = base64.b64encode(sig_bytes).decode()
#         vault_sig = f"vault:v1:{sig_b64_std}"
#         is_valid = self.verify_signature(key_name, signing_input, vault_sig)
#         payload_json = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)).decode()
#         claims = json.loads(payload_json) if is_valid else {}
#         return is_valid, claims

#     # Public key KV storage
#     def store_public_key_metadata(self, key_id: str, public_key_pem: str, meta: Optional[Dict[str, Any]] = None) -> str:
#         path = f"public-keys/{key_id}"
#         secret_data = {
#             "public_key": public_key_pem,
#             "created_at": datetime.now(timezone.utc).isoformat(),
#         }
#         if meta:
#             secret_data.update({"meta": meta})
#         self.client.secrets.kv.v2.create_or_update_secret(
#             path=path, secret=secret_data, mount_point=self.kv_mount
#         )
#         return f"{self.kv_mount}/data/{path}"

#     def read_public_key_metadata(self, key_id: str) -> Optional[Dict[str, Any]]:
#         path = f"public-keys/{key_id}"
#         try:
#             response = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=self.kv_mount)
#             return response["data"]["data"]
#         except exceptions.InvalidPath:
#             return None

# # Użycie: vault = VaultService(url, token)
