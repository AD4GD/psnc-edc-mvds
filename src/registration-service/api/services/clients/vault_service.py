import logging
import hvac
import base64
from api.core.settings import KeyVaultSettings

# TODO test code because AI generated

logger = logging.getLogger(__name__)

class VaultService:
    """Synchronous service for interacting with HashiCorp Vault."""

    def __init__(self):
        self.client = hvac.Client(url=KeyVaultSettings.vault_url, token=KeyVaultSettings.vault_token)
        if not self.client.is_authenticated():
            raise RuntimeError("Vault authentication failed")
        # KV mount for secrets (KV v2)
        self.kv_mount = KeyVaultSettings.vault_kv_mount
        # Transit mount for crypto operations (default to 'transit' if not provided)
        self.transit_mount = getattr(KeyVaultSettings, "vault_transit_mount", "transit")

    def health(self) -> bool:
        """Check Vault server health."""
        try:
            health : dict = self.client.sys.read_health_status(method='GET')
            return health.get("initialized", False)
        except Exception as e:
            logger.error(f"Vault health check failed: {e}")
            return False

    def store_public_key(self, key_id: str, public_pem: bytes) -> str:
        """Store public key in Vault (KV v2)."""
        path = f"keys/{key_id}"
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret={"public_key": public_pem.decode()},
            mount_point=self.kv_mount
        )
        return f"{self.kv_mount}/data/{path}"

    def read_public_key(self, key_id: str) -> str | None:
        """Read public key from Vault (KV v2)."""
        path = f"keys/{key_id}"
        try:
            data = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=self.kv_mount)
            return data["data"]["data"].get("public_key")
        except Exception as e:
            logger.error(f"Vault read_public_key failed: {e}")
            return None

    # ----- Transit (sign/encrypt) helpers -----
    def create_transit_key(self, key_name: str, key_type: str = "ed25519", exportable: bool = False) -> dict:
        """Create a transit key (if not exists). Returns API response."""
        try:
            return self.client.secrets.transit.create_key(
                name=key_name,
                type=key_type,
                exportable=exportable,
                mount_point=self.transit_mount
            )
        except Exception as e:
            logger.warning(f"create_transit_key failed (might already exist): {e}")
            return {}

    def sign_bytes(self, key_name: str, data: bytes) -> str:
        """
        Sign arbitrary bytes using Vault Transit.
        Returns Vault signature string (e.g. 'vault:v1:BASE64...').
        NOTE: Vault transit.sign_data expects input_b64 (base64 of plaintext or pre-hash depending on key/algorithm).
        """
        try:
            input_b64 = base64.b64encode(data).decode()
            resp = self.client.secrets.transit.sign_data(
                name=key_name,
                input_b64=input_b64,
                mount_point=self.transit_mount
            )
            return resp["data"]["signature"]
        except Exception as e:
            logger.error(f"Vault sign_bytes failed: {e}")
            raise

    def verify_signature(self, key_name: str, data: bytes, signature: str) -> bool:
        """Verify signature created by Vault Transit."""
        try:
            input_b64 = base64.b64encode(data).decode()
            resp = self.client.secrets.transit.verify_signed_data(
                name=key_name,
                input_b64=input_b64,
                signature=signature,
                mount_point=self.transit_mount
            )
            return resp.get("data", {}).get("valid", False)
        except Exception as e:
            logger.error(f"Vault verify_signature failed: {e}")
            return False

    def encrypt_bytes(self, key_name: str, plaintext: bytes) -> str:
        """
        Encrypt bytes using Vault Transit.
        Returns ciphertext string (Vault format).
        """
        try:
            plaintext_b64 = base64.b64encode(plaintext).decode()
            resp = self.client.secrets.transit.encrypt_data(
                name=key_name,
                plaintext=plaintext_b64,
                mount_point=self.transit_mount
            )
            return resp["data"]["ciphertext"]
        except Exception as e:
            logger.error(f"Vault encrypt_bytes failed: {e}")
            raise

    def decrypt_bytes(self, key_name: str, ciphertext: str) -> bytes:
        """
        Decrypt a Vault Transit ciphertext and return plaintext bytes.
        """
        try:
            resp = self.client.secrets.transit.decrypt_data(
                name=key_name,
                ciphertext=ciphertext,
                mount_point=self.transit_mount
            )
            plaintext_b64 = resp["data"]["plaintext"]
            return base64.b64decode(plaintext_b64)
        except Exception as e:
            logger.error(f"Vault decrypt_bytes failed: {e}")
            raise

    # ----- Generic KV helpers -----
    def store_secret(self, path: str, secret: dict) -> str:
        """Store arbitrary secret dict in KV v2 and return path reference."""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret,
                mount_point=self.kv_mount
            )
            return f"{self.kv_mount}/data/{path}"
        except Exception as e:
            logger.error(f"Vault store_secret failed: {e}")
            raise

    def read_secret(self, path: str) -> dict | None:
        """Read secret data dict from KV v2 path."""
        try:
            data = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=self.kv_mount)
            return data["data"]["data"]
        except Exception as e:
            logger.error(f"Vault read_secret failed: {e}")
            return None

vault_service = VaultService()
