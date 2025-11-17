# api/services/vault_init.py
"""
HashiCorp Vault initialization module for DCP/VC operations.

This module provides utilities to initialize Vault with required secrets engines,
policies, and keys for Verifiable Credentials and DCP operations.
"""

import sys
from typing import Any, Dict, List, Optional

from api.core.logging_config import setup_logging
from api.core.settings import KeyVaultSettings
from hvac.exceptions import InvalidRequest

from .vault_service import VaultService

logger = setup_logging()


class VaultInitializer:
    """Initialize and configure HashiCorp Vault for production use."""

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize Vault client for setup operations.

        Args:
            url: Vault server URL (defaults to settings)
            token: Vault token with admin privileges (defaults to settings)
        """
        self.vault = VaultService()
        # self.vault_url = url or KeyVaultSettings.vault_url
        # self.vault_token = token or KeyVaultSettings.vault_token

        # self.client = hvac.Client(url=self.vault_url, token=self.vault_token)

        if not self.vault.client.is_authenticated():
            raise RuntimeError(f"Vault authentication failed for {KeyVaultSettings.vault_url}")

        logger.info(f"VaultInitializer connected to {KeyVaultSettings.vault_url}")

    def check_vault_status(self) -> bool:
        """
        Check Vault server status.

        Returns:
            Dict with initialized, sealed, and other status info
        """
        try:
            return self.vault.health()
        except Exception as e:
            logger.error(f"Failed to check Vault status: {e}")
            raise

    def enable_secrets_engine(
        self, engine_type: str, path: str, description: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enable a secrets engine at specified path.

        Args:
            engine_type: Type of engine (kv, transit, pki, etc.)
            path: Mount path for the engine
            description: Human-readable description
            config: Engine-specific configuration

        Returns:
            True if enabled, False if already exists
        """
        try:
            self.vault.client.sys.enable_secrets_engine(
                backend_type=engine_type, path=path, description=description, config=config
            )
            logger.info(f"✓ Enabled {engine_type} secrets engine at '{path}'")
            return True

        except InvalidRequest as e:
            if "path is already in use" in str(e):
                logger.info(f"⚠ Secrets engine already enabled at '{path}'")
                return True
            raise

    def configure_kv_engine(
        self,
        mount_point: str = "secret",
        max_versions: int = 10,
        cas_required: bool = False,
        delete_version_after: str = "0s",
    ) -> None:
        """
        Configure KV v2 secrets engine.

        Args:
            mount_point: KV mount path
            max_versions: Maximum number of versions to keep
            cas_required: Require Check-And-Set for writes
            delete_version_after: Duration before versions are deleted (e.g., "3h", "30d")
        """
        try:
            self.vault.client.sys.tune_mount_configuration(path=mount_point, max_lease_ttl="0", default_lease_ttl="0")

            # Configure KV-specific settings
            self.vault.client.secrets.kv.v2.configure(
                max_versions=max_versions,
                cas_required=cas_required,
                delete_version_after=delete_version_after,
                mount_point=mount_point,
            )

            logger.info(f"✓ Configured KV engine at '{mount_point}' (max_versions={max_versions})")

        except Exception as e:
            logger.error(f"Failed to configure KV engine: {e}")
            raise

    def create_transit_key(
        self,
        key_name: str,
        key_type: str = "ed25519",
        mount_point: str = "transit",
        exportable: bool = False,
        allow_plaintext_backup: bool = False,
        auto_rotate_period: Optional[str] = None,
    ) -> bool:
        """
        Create a transit encryption/signing key.

        Args:
            key_name: Name for the key
            key_type: Type (ed25519, ecdsa-p256, rsa-2048, aes256-gcm96, etc.)
            mount_point: Transit mount path
            exportable: Allow key export
            allow_plaintext_backup: Allow plaintext backup
            auto_rotate_period: Auto-rotation period (e.g., "720h" for 30 days)

        Returns:
            True if created, False if already exists
        """
        try:
            self.vault.transit.create_key(
                name=key_name,
                convergent_encryption=False,
                derived=False,
                exportable=exportable,
                allow_plaintext_backup=allow_plaintext_backup,
                key_type=key_type,
                mount_point=mount_point,
                auto_rotate_period=auto_rotate_period,
            )
            logger.info(f"✓ Created transit key '{key_name}' (type={key_type})")
            return True

        except InvalidRequest as e:
            if "already exists" in str(e):
                logger.warning(f"⚠ Transit key '{key_name}' already exists")
                return False
            raise

    def create_policy(self, policy_name: str, policy_rules: str) -> None:
        """
        Create or update a Vault policy.

        Args:
            policy_name: Name of the policy
            policy_rules: HCL policy rules as string
        """
        try:
            self.vault.client.sys.create_or_update_policy(name=policy_name, policy=policy_rules)
            logger.info(f"✓ Created policy '{policy_name}'")

        except Exception as e:
            logger.error(f"Failed to create policy '{policy_name}': {e}")
            raise

    def create_vc_signer_policy(self) -> None:
        """Create policy for Verifiable Credential signing operations."""
        policy_rules = """
# Policy for Verifiable Credential signing

# Read and list signing keys
path "transit/keys/*" {
  capabilities = ["read", "list"]
}

# Sign data with issuer keys
path "transit/sign/issuer-*" {
  capabilities = ["update"]
}

# Verify signatures
path "transit/verify/*" {
  capabilities = ["update"]
}

# Create and rotate keys
path "transit/keys/issuer-*" {
  capabilities = ["create", "update"]
}

# Store and read public keys
path "secret/data/public-keys/*" {
  capabilities = ["create", "read", "update", "list"]
}

# Metadata operations
path "secret/metadata/public-keys/*" {
  capabilities = ["list", "read", "delete"]
}

# Store VC metadata
path "secret/data/vc-metadata/*" {
  capabilities = ["create", "read", "update", "list"]
}
"""
        self.create_policy("vc-signer", policy_rules)

    def create_vc_verifier_policy(self) -> None:
        """Create policy for read-only VC verification."""
        policy_rules = """
# Policy for Verifiable Credential verification (read-only)

# Read public keys
path "transit/keys/*" {
  capabilities = ["read"]
}

# Verify signatures only
path "transit/verify/*" {
  capabilities = ["update"]
}

# Read public key metadata
path "secret/data/public-keys/*" {
  capabilities = ["read", "list"]
}

path "secret/metadata/public-keys/*" {
  capabilities = ["list", "read"]
}

# Read VC metadata
path "secret/data/vc-metadata/*" {
  capabilities = ["read", "list"]
}
"""
        self.create_policy("vc-verifier", policy_rules)

    def create_app_token(
        self,
        policies: List[str],
        display_name: str,
        ttl: Optional[str] = None,
        renewable: bool = True,
        meta: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create an application token with specific policies.

        Args:
            policies: List of policy names to attach
            display_name: Display name for the token
            ttl: Time to live (e.g., "24h", "720h")
            renewable: Whether token can be renewed
            meta Additional metadata

        Returns:
            Dict with 'token' and token info
        """
        try:
            response = self.vault.client.auth.token.create(
                policies=policies, ttl=ttl, renewable=renewable, display_name=display_name, meta=meta or {}
            )

            token_info = {
                "token": response["auth"]["client_token"],
                "accessor": response["auth"]["accessor"],
                "policies": response["auth"]["policies"],
                "renewable": response["auth"]["renewable"],
                "ttl": response["auth"]["lease_duration"],
            }

            logger.info(f"✓ Created token for '{display_name}' with policies: {policies}")
            return token_info

        except Exception as e:
            logger.error(f"Failed to create token: {e}")
            raise

    def setup_for_vc_operations(
        self, kv_mount: str = "secret", transit_mount: str = "transit", create_default_keys: bool = True
    ) -> Dict[str, Any]:
        """
        Complete setup for Verifiable Credential operations.

        Args:
            kv_mount: KV secrets engine mount point
            transit_mount: Transit engine mount point
            create_default_keys: Create default signing/encryption keys

        Returns:
            Dict with setup summary
        """
        _summary = {"engines_enabled": [], "policies_created": [], "keys_created": [], "errors": []}

        try:
            logger.info("=" * 60)
            logger.info("Starting Vault setup for VC operations...")
            logger.info("=" * 60)

            # 1. Enable KV v2 engine
            if self.enable_secrets_engine("kv", kv_mount, "KV v2 for secrets", {"version": "2"}):
                _summary["engines_enabled"].append(f"kv-v2:{kv_mount}")

            # 2. Configure KV engine
            self.configure_kv_engine(mount_point=kv_mount, max_versions=10, cas_required=False)

            # 3. Enable Transit engine
            if self.enable_secrets_engine("transit", transit_mount, "Transit for crypto operations"):
                _summary["engines_enabled"].append(f"transit:{transit_mount}")

            # 4. Create policies
            self.create_vc_signer_policy()
            _summary["policies_created"].append("vc-signer")

            self.create_vc_verifier_policy()
            _summary["policies_created"].append("vc-verifier")

            # 5. Create default keys if requested
            if create_default_keys:
                # Main issuer signing key (Ed25519 for VC)
                if self.create_transit_key(
                    key_name="issuer-main-key",
                    key_type="ed25519",
                    mount_point=transit_mount,
                    exportable=False,
                    auto_rotate_period="2160h",  # 90 days
                ):
                    _summary["keys_created"].append("issuer-main-key (ed25519)")

                # Secondary ECDSA key for compatibility
                if self.create_transit_key(
                    key_name="issuer-ecdsa-key", key_type="ecdsa-p256", mount_point=transit_mount, exportable=False
                ):
                    _summary["keys_created"].append("issuer-ecdsa-key (ecdsa-p256)")

                # Data encryption key
                if self.create_transit_key(
                    key_name="data-encryption-key", key_type="aes256-gcm96", mount_point=transit_mount, exportable=False
                ):
                    _summary["keys_created"].append("data-encryption-key (aes256-gcm96)")

            logger.info("=" * 60)
            logger.info("✅ Vault setup completed successfully!")
            logger.info("=" * 60)
            logger.info(f"Engines enabled: {_summary['engines_enabled']}")
            logger.info(f"Policies created: {_summary['policies_created']}")
            logger.info(f"Keys created: {_summary['keys_created']}")

            return _summary

        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            _summary["errors"].append(str(e))
            raise

    def cleanup(
        self,
        disable_engines: bool = False,
        delete_policies: bool = False,
        kv_mount: str = "secret",
        transit_mount: str = "transit",
    ) -> None:
        """
        Cleanup Vault configuration (USE WITH CAUTION).

        Args:
            disable_engines: Disable secrets engines
            delete_policies: Delete created policies
            kv_mount: KV mount to disable
            transit_mount: Transit mount to disable
        """
        logger.warning("⚠️  Starting Vault cleanup (DESTRUCTIVE OPERATION)")

        if delete_policies:
            for _policy in ["vc-signer", "vc-verifier"]:
                self.vault.client.sys.delete_policy(_policy)
                logger.info(f"✓ Deleted policy '{_policy}'")

        if disable_engines:
            for mount in [kv_mount, transit_mount]:
                self.vault.client.sys.disable_secrets_engine(mount)
                logger.info(f"✓ Disabled secrets engine '{mount}'")

        logger.info("✅ Cleanup completed")


def initialize_vault(
    url: Optional[str] = None, token: Optional[str] = None, create_default_keys: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to initialize Vault with default settings.

    Args:
        url: Vault URL (optional, uses settings)
        token: Vault token (optional, uses settings)
        create_default_keys: Create default signing/encryption keys

    Returns:
        Setup summary dict

    Example:
        >>> from api.services.vault_init import initialize_vault
        >>> summary = initialize_vault()
        >>> print(f"Created keys: {summary['keys_created']}")
    """
    initializer = VaultInitializer(url=url, token=token)
    return initializer.setup_for_vc_operations(create_default_keys=create_default_keys)


if __name__ == "__main__":
    # Allow running as script

    try:
        _summary = initialize_vault(create_default_keys=True)
        logger.info("\n" + "=" * 60)
        logger.info("VAULT INITIALIZATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Engines enabled: {len(_summary['engines_enabled'])}")
        for engine in _summary["engines_enabled"]:
            logger.info(f"  • {engine}")
        logger.info(f"\nPolicies created: {len(_summary['policies_created'])}")
        for _policy in _summary["policies_created"]:
            logger.info(f"  • {_policy}")
        logger.info(f"\nKeys created: {len(_summary['keys_created'])}")
        for key in _summary["keys_created"]:
            logger.info(f"  • {key}")
        logger.info("=" * 60)
        sys.exit(0)

    except Exception as e:
        logger.error(f"\n❌ Initialization failed: {e}", file=sys.stderr)
        sys.exit(1)
