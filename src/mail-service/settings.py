from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    X_API_KEY: str = Field(..., alias="X_API_KEY")
    MAIL_USERNAME: str = Field(..., alias="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., alias="MAIL_PASSWORD")
    MAIL_FROM: str = Field("", alias="MAIL_FROM")
    MAIL_PORT: int = Field(587, alias="MAIL_PORT")
    MAIL_SERVER: str = Field(..., alias="MAIL_SERVER")
    MAIL_FROM_NAME: str = Field("", alias="MAIL_FROM_NAME")
    MAIL_STARTTLS: bool = Field(True, alias="MAIL_STARTTLS")
    MAIL_SSL_TLS: bool = Field(False, alias="MAIL_SSL_TLS")
    USE_CREDENTIALS: bool = Field(True, alias="USE_CREDENTIALS")
    VALIDATE_CERTS: bool = Field(True, alias="VALIDATE_CERTS")
    TEMPLATE_FOLDER: str = Field("", alias="TEMPLATE_FOLDER")

    class Config:
        env_file = ".env"


Settings_ = Settings()
