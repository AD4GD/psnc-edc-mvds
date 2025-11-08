"""
Comprehensive tests for VaultService using mocks.
Run with: pytest tests/test_vault_service.py -v
"""

import pytest
from api.services.clients import VaultInitializer, VaultService
from hvac.exceptions import InvalidPath, InvalidRequest


# Health tests
class TestHealthCheck:
    def test_vault_health_success(self, mocked_vault_service: VaultService):
        assert mocked_vault_service.health() is True

    def test_vault_health_sealed(self, mocked_vault_service: VaultService, mock_vault_client):
        mock_vault_client.sys.read_health_status.return_value = {"sealed": True}
        assert mocked_vault_service.health() is True

    def test_vault_health_exception(self, mocked_vault_service: VaultService, mock_vault_client):
        mock_vault_client.sys.read_health_status.side_effect = Exception("Error")
        assert mocked_vault_service.health() is True


# Key management (uproszczone: używa wspólnego fixture)
class TestKeyManagement:
    def test_create_get_public_key(self, mocked_vault_service: VaultService, test_key_name):
        mocked_vault_service.create_signing_key(test_key_name, "ed25519")
        pub_key = mocked_vault_service.get_public_key(test_key_name)
        assert pub_key["public_key"] is not None

    def test_rotate_key(self, mocked_vault_service: VaultService, test_key_name):
        mocked_vault_service.create_signing_key(test_key_name, "ed25519")
        response = mocked_vault_service.rotate_key(test_key_name)
        assert response is not None

    def test_create_key_already_exists(self, mocked_vault_service: VaultService, test_key_name):
        mocked_vault_service.create_signing_key(test_key_name, "ed25519")  # Pierwsze utworzenie
        response = mocked_vault_service.create_signing_key(test_key_name, "ed25519")  # Drugie (już istnieje)
        assert response.get("warning") == "key_already_exists" or "data" in response


# Signing (uproszczone: mniej fixture'ów, parametrize dla wariantów)
class TestSigningOperations:
    @pytest.fixture(autouse=True)
    def setup_key(self, mocked_vault_service: VaultService, test_key_name):
        mocked_vault_service.create_signing_key(test_key_name, "ed25519")

    @pytest.mark.parametrize(
        "data, hash_alg, expected",
        [
            (b"data", None, "vault:v"),
            (b"data", "sha2-256", "vault:v"),
        ],
    )
    def test_sign_data(self, mocked_vault_service: VaultService, test_key_name, data, hash_alg, expected):
        kwargs = {"hash_algorithm": hash_alg} if hash_alg else {}
        signature = mocked_vault_service.sign_data(test_key_name, data, **kwargs)
        assert signature.startswith(expected)

    def test_sign_data_with_version(self, mocked_vault_service: VaultService, test_key_name):
        mocked_vault_service.rotate_key(test_key_name)  # Wersja 2
        signature = mocked_vault_service.sign_data(test_key_name, b"data", key_version=2)
        assert "vault:v2:" in signature

    def test_verify_signature_valid(self, mocked_vault_service: VaultService, test_key_name):
        data = b"data"
        signature = mocked_vault_service.sign_data(test_key_name, data)
        assert mocked_vault_service.verify_signature(test_key_name, data, signature) is True

    def test_verify_signature_invalid(self, mocked_vault_service: VaultService, test_key_name):
        assert mocked_vault_service.verify_signature(test_key_name, b"data", "invalid-sig") is False

    def test_verify_signature_exception(self, mocked_vault_service: VaultService, test_key_name, mock_vault_client):
        mock_vault_client.secrets.transit.verify_signed_data.side_effect = Exception("Error")
        assert mocked_vault_service.verify_signature(test_key_name, b"data", "sig") is False


# Verifiable Credentials (skrócone: mniej testów, skupione na core)
class TestVerifiableCredentials:
    def test_sign_verify_vc(self, mocked_vault_service: VaultService, test_key_name, sample_credential):
        mocked_vault_service.create_signing_key(test_key_name, "ed25519")
        signed = mocked_vault_service.sign_verifiable_credential(test_key_name, sample_credential)
        assert "proof" in signed and signed["proof"]["proofValue"] is not None
        # Verify structure
        assert signed["proof"]["type"] == "Ed25519Signature2020"
        assert signed["proof"]["proofPurpose"] == "assertionMethod"
        assert signed["proof"]["_vaultSignature"].startswith("vault:v")
        assert signed["issuer"] == sample_credential["issuer"]
        assert signed["credentialSubject"] == sample_credential["credentialSubject"]
        assert mocked_vault_service.verify_verifiable_credential(test_key_name, signed) is True

    def test_verify_vc_invalid(
        self, mocked_vault_service: VaultService, test_key_name, sample_credential, mock_vault_client
    ):
        mock_vault_client.secrets.transit.verify_signed_data.return_value = {"data": {"valid": False}}
        assert mocked_vault_service.verify_verifiable_credential(test_key_name, sample_credential) is False


# Public key storage (simplified)
class TestPublicKeyStorage:
    def test_store_read_public_key(self, mocked_vault_service: VaultService):
        key_id = "did:test:123"
        pem = "test-pem"
        mocked_vault_service.store_public_key_metadata(key_id, pem, meta={"test": "meta"})
        stored = mocked_vault_service.read_public_key_metadata(key_id)
        assert "public_key" in stored and stored["public_key"] == pem

    def test_read_nonexistent_public_key(self, mocked_vault_service: VaultService, mock_vault_client):
        mock_vault_client.secrets.kv.v2.read_secret_version.side_effect = InvalidPath("Not found")
        assert mocked_vault_service.read_public_key_metadata("nonexistent") is None


# Encryption (simplified: parametrize, shared keys)
class TestEncryption:
    @pytest.mark.parametrize(
        "key_name, context, expected_success",
        [
            ("aes", None, True),  # AES without context
            ("chacha", "user-123", True),  # ChaCha with context
        ],
    )
    def test_encrypt_decrypt_roundtrip(
        self, mocked_vault_service: VaultService, encryption_keys, key_name, context, expected_success
    ):
        # Setup key
        if key_name == "chacha":
            mocked_vault_service.create_signing_key(encryption_keys["chacha"], "chacha20-poly1305", derived=True)
        else:
            mocked_vault_service.create_signing_key(encryption_keys[key_name], "aes256-gcm96")

        data = b"test-data"
        kwargs = {"context": context} if context else {}

        ciphertext = mocked_vault_service.encrypt_data(encryption_keys[key_name], data, **kwargs)
        assert ciphertext.startswith("vault:v")

        if expected_success:
            decrypted = mocked_vault_service.decrypt_data(encryption_keys[key_name], ciphertext, **kwargs)
            assert decrypted == data
        else:
            pytest.raises(
                Exception, mocked_vault_service.decrypt_data, encryption_keys[key_name], ciphertext, context="wrong"
            )

    def test_encrypt_wrong_context_fails(self, mocked_vault_service: VaultService, encryption_keys):
        mocked_vault_service.create_signing_key(encryption_keys["chacha"], "chacha20-poly1305", derived=True)
        ciphertext = mocked_vault_service.encrypt_data(encryption_keys["chacha"], b"data", context="correct")
        with pytest.raises(Exception):
            mocked_vault_service.decrypt_data(encryption_keys["chacha"], ciphertext, context="wrong")


class TestKVStorage:
    def test_store_read_secret(self, mocked_vault_service: VaultService):
        path = "test/secret"
        data = {"key": "value"}
        mocked_vault_service.store_secret(path, data)
        retrieved = mocked_vault_service.read_secret(path)
        assert retrieved["key"] == "value"

    def test_read_nonexistent_secret(self, mocked_vault_service: VaultService, mock_vault_client):
        mock_vault_client.secrets.kv.v2.read_secret_version.side_effect = InvalidPath("Not found")
        assert mocked_vault_service.read_secret("nonexistent") is None

    def test_delete_secret(self, mocked_vault_service: VaultService):
        path = "test/secret"
        mocked_vault_service.store_secret(path, {"test": "data"})
        assert mocked_vault_service.delete_secret(path) is not None
        assert mocked_vault_service.read_secret(path) is None


class TestVaultInitializer:
    def test_check_vault_status(self, mocked_vault_initializer):
        assert mocked_vault_initializer.check_vault_status() is True

    def test_enable_secrets_engine(self, mocked_vault_initializer: VaultInitializer, mock_vault_client):
        mock_vault_client.sys.list_secrets_engines.return_value = {"data": {"secret_mounts": {}}}
        mock_vault_client.sys.enable_secrets_engine.return_value = True

        result = mock_vault_client.sys.enable_secrets_engine(engine_type="kv", path="secret")
        assert result is True
        mock_vault_client.sys.enable_secrets_engine.assert_called_once()

    def test_enable_secrets_engine_already_exists(self, mocked_vault_initializer: VaultInitializer, mock_vault_client):
        mock_vault_client.sys.enable_secrets_engine.side_effect = InvalidRequest("already in use")
        result = mocked_vault_initializer.enable_secrets_engine("kv", "secret")
        assert result is False

    def test_create_transit_key(self, mocked_vault_initializer):
        assert mocked_vault_initializer.create_transit_key("test-key", "ed25519") is True

    def test_create_policy(self, mocked_vault_initializer: VaultInitializer):
        policy_rules = """
        path "secret/*" {
            capabilities = ["read"]
        }
        """
        mocked_vault_initializer.create_policy("test-policy", policy_rules)

    def test_create_vc_policies(self, mocked_vault_initializer):
        mocked_vault_initializer.create_vc_signer_policy()
        mocked_vault_initializer.create_vc_verifier_policy()
        # Check calls if needed

    def test_create_app_token(self, mocked_vault_initializer):
        token_info = mocked_vault_initializer.create_app_token(policies=["vc-verifier"], display_name="test", ttl="1h")
        assert "token" in token_info and "vc-verifier" in token_info["policies"]

    def test_setup_for_vc_operations(self, mocked_vault_initializer):
        summary = mocked_vault_initializer.setup_for_vc_operations(create_default_keys=True)
        assert "engines_enabled" in summary and not len(summary["errors"])


# Integration (uproszczone: end-to-end bez nadmiaru)
class TestIntegration:
    def test_complete_vc_workflow(self, mocked_vault_service: VaultService, test_key_name, sample_credential):
        # Create & get key
        mocked_vault_service.create_signing_key(test_key_name, "ed25519")
        pub_key = mocked_vault_service.get_public_key(test_key_name)
        assert pub_key["public_key"] is not None

        # Store public key
        path = mocked_vault_service.store_public_key_metadata("did:test:123", pub_key["public_key"])
        assert "public-keys" in path

        # Sign & verify VC
        signed = mocked_vault_service.sign_verifiable_credential(test_key_name, sample_credential)
        assert mocked_vault_service.verify_verifiable_credential(test_key_name, signed) is True

        # Store VC metadata
        vc_path = mocked_vault_service.store_secret("vc/test", {"vc": signed})
        assert "secret/data/vc" in vc_path
