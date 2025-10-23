from enum import Enum
from pydantic import Field
from pydantic_settings import BaseSettings


class ProjectSettings(BaseSettings):
    service_name: str = Field(..., alias="SERVICE_NAME")
    issuer_did: str = Field(..., alias="ISSUER_DID")
    port: int = Field(8000, alias="API_PORT")
    service_version: str = "0.0.0"

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
    vault_url: str = Field(..., alias="VAULT_URL")
    vault_role_id: str = Field(..., alias="VAULT_ROLE_ID")
    vault_secret_id: str = Field(..., alias="VAULT_SECRET_ID")
    vault_kv_mount: str = Field(..., alias="VAULT_KV_MOUNT")
    vault_token: str = Field(..., alias="VAULT_TOKEN")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


class DigitalWalletSettings(BaseSettings):
    dw_endpoint: str = Field(..., alias="DIGITAL_WALLET_ENDPOINT")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


ProjectSettings = ProjectSettings()
PostgreSQLSettings = PostgreSQLSettings()
KeycloakSettings = KeycloakSettings()
DigitalWalletSettings = DigitalWalletSettings()
