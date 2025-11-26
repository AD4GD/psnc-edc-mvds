from api.models.dto.local import KeyTypeEnum
from pydantic import Field
from pydantic_settings import BaseSettings


class ProjectSettings(BaseSettings):
    service_name: str = Field(..., alias="SERVICE_NAME")
    issuer_did: str = Field(..., alias="ISSUER_DID")
    port: int = Field(8000, alias="API_PORT")
    service_version: str = "0.0.0"
    frontend_url: str = Field("http://localhost", alias="FRONTEND_URL")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


class PostgreSQLSettings(BaseSettings):
    postgres_host: str = Field(..., alias="POSTGRESQL_HOST")
    postgres_port: int = Field(..., alias="POSTGRESQL_PORT")
    postgres_db: str = Field(..., alias="POSTGRESQL_DB")
    postgres_user: str = Field(..., alias="POSTGRESQL_USERNAME")
    postgres_password: str = Field(..., alias="POSTGRESQL_PASSWORD")

    @property
    def postgres_uri(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


class KeycloakSettings(BaseSettings):
    keycloak_server_url: str = Field(..., alias="KEYCLOAK_SERVER_URL")
    keycloak_realm: str = Field(..., alias="KEYCLOAK_REALM")
    keycloak_client_id: str = Field(..., alias="KEYCLOAK_CLIENT_ID")
    keycloak_client_secret: str = Field(..., alias="KEYCLOAK_CLIENT_SECRET")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


class KeyVaultSettings(BaseSettings):
    vault_url: str = Field("http://localhost:8200", alias="VAULT_URL")
    vault_role_id: str = Field(..., alias="VAULT_ROLE_ID")
    vault_secret_id: str = Field(..., alias="VAULT_SECRET_ID")
    vault_kv_mount: str = Field(..., alias="VAULT_KV_MOUNT")
    vault_token: str = Field("vault_token", alias="VAULT_TOKEN")
    # Optional: Namespace for Vault Enterprise
    vault_namespace: str = Field("vault_namespace", alias="VAULT_NAMESPACE")
    # Default key settings
    key_name: str = Field("key_name", alias="KEY_NAME")
    default_key_type: str = Field(KeyTypeEnum.ED25519, alias="DEFAULT_KEY_TYPE")  # For VC signing
    encryption_key_name: str = Field("encryption_key", alias="ENCRYPTION_KEY_NAME")
    default_encryption_key_type: str = Field(KeyTypeEnum.AES256_GCM96, alias="DEFAULT_ENCRYPTION_KEY_TYPE")  # For encryption
    vault_key_auto_rotate_days: int = Field(90, alias="VAULT_KEY_AUTO_ROTATE_DAYS")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


class VerifiableCredentialsSettings(BaseSettings):
    vc_issuer_did: str = Field(..., alias="ISSUER_DID")
    contract_version: str = Field("1.0.0", alias="VC_CONTRACT_VERSION")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


class EmailServiceSettings(BaseSettings):
    email_svc_endpoint: str = Field(..., alias="EMAIL_SERVICE_SEND_EMAIL_ENDPOINT")
    email_api_key: str = Field(..., alias="EMAIL_SERVICE_API_KEY")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


ProjectSettings = ProjectSettings()
PostgreSQLSettings = PostgreSQLSettings()
KeycloakSettings = KeycloakSettings()
KeyVaultSettings = KeyVaultSettings()
VerifiableCredentialsSettings = VerifiableCredentialsSettings()
EmailServiceSettings = EmailServiceSettings()
