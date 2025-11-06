# tests/conftest.py
"""
Pytest configuration and fixtures for Vault tests.
"""

import pytest
import os
import sys
import base64
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Dict, Any
from hvac.exceptions import InvalidRequest, InvalidPath

# Add project root to path
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Environment setup
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    os.environ["VAULT_URL"] = "http://localhost:7200"
    os.environ["VAULT_TOKEN"] = "test-token"
    os.environ["VAULT_KV_MOUNT"] = "secret"
    os.environ["VAULT_TRANSIT_MOUNT"] = "transit"
    yield

@pytest.fixture(scope="session")
def vault_url() -> str:
    return os.getenv("VAULT_URL", "http://localhost:7200")

@pytest.fixture(scope="session")
def vault_token() -> str:
    return os.getenv("VAULT_TOKEN", "test-token")

# Common key name fixture (class scope - shared per class)
@pytest.fixture(scope="class")
def test_key_name():
    import uuid
    return f"test-key-{uuid.uuid4().hex[:8]}"

# Common encryption keys (class scope)
@pytest.fixture(scope="class")
def encryption_keys():
    import uuid
    return {
        "aes": f"test-aes-{uuid.uuid4().hex[:8]}",
        "chacha": f"test-chacha-{uuid.uuid4().hex[:8]}"
    }

# Sample VC fixture
@pytest.fixture
def sample_credential() -> Dict[str, Any]:
    return {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "type": ["VerifiableCredential"],
        "issuer": "did:example:issuer",
        "issuanceDate": "2024-01-01T00:00:00Z",
        "credentialSubject": {"id": "did:example:subject", "name": "Test User"}
    }

# Mock Vault client (uproszczony, kompleksowy)
@pytest.fixture
def mock_vault_client():
    client = MagicMock()
    client.is_authenticated.return_value = True
    client.token = "test-token"
    client.url = "http://localhost:7200"

    # Health
    client.sys.read_health_status.return_value = {"initialized": True, "sealed": False}

    # Transit
    transit = MagicMock()
    transit.create_key.return_value = {"data": {}}  # Obsługa derived=True
    transit.read_key.return_value = {
        "data": {"type": "ed25519", "latest_version": 1, "keys": {"1": {"public_key": "test-pem"}}}
    }
    transit.list_keys.return_value = {"data": {"keys": ["test-key"]}}
    transit.sign_data.return_value = {"data": {"signature": "vault:v1:test-sig"}}
    transit.verify_signed_data.return_value = {"data": {"valid": True}}
    transit.rotate_key.return_value = {"data": {}}
    transit.encrypt_data.return_value = {"data": {"ciphertext": "vault:v1:encrypted"}}
    transit.decrypt_data.return_value = {"data": {"plaintext": base64.b64encode(b"test").decode()}}
    transit.delete_key.return_value = {"data": {}}
    client.secrets.transit = transit

    # KV v2
    kv = MagicMock()
    kv.create_or_update_secret.return_value = {"data": {}}
    kv.read_secret_version.return_value = {
        "data": {"data": {"username": "test", "password": "pass", "public_key": "pem"}}
    }
    kv.delete_latest_version_of_secret.return_value = {"data": {}}
    kv.delete_secret_versions.return_value = {"data": {}}
    kv.configure.return_value = {"data": {"options": {"max_versions": 10}}}
    # Ustaw default dla delete_version_after="0s", cas_required=False
    kv.configure.side_effect = lambda **kwargs: {"data": {"options": kwargs}}
    kv.configure.return_value = {"data": {
        "options": {"version": "2", "max_versions": 10}
    }}
    client.secrets.kv.v2 = kv

    # Sys
    sys_mock = MagicMock()
    sys_mock.list_secrets_engines.return_value = {"data": {"secret_mounts": {}}}
    # sys_mock.enable_secrets_engine.return_value = {"data": {}}
    sys_mock.tune_mount_configuration.return_value = {"data": {}}
    sys_mock.create_or_update_policy.return_value = {"data": {}}
    sys_mock.delete_policy.return_value = {"data": {}}
    sys_mock.list_policies.return_value = {"data": {"policies": ["default"]}}
    client.sys = sys_mock

    # Auth token
    client.auth.token.create.return_value = {
        "auth": {"client_token": "hvs.test", "policies": ["vc-verifier"], "lease_duration": 3600}
    }

    return client

# Mocked services
@pytest.fixture
def mocked_vault_service(mock_vault_client):
    with patch('hvac.Client', return_value=mock_vault_client):
        from api.services.clients import VaultService
        return VaultService()

@pytest.fixture
def mocked_vault_initializer(mock_vault_client):
    """Create VaultInitializer with mocked client."""
    with patch('hvac.Client', return_value=mock_vault_client):
        from api.services.clients import VaultInitializer
        return VaultInitializer()
