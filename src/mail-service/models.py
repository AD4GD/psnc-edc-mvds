from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class EmailConfig(BaseModel):
    MAIL_USERNAME: str = Field(None, description="username")
    MAIL_PASSWORD: str = Field(None, description="password")
    MAIL_FROM: Optional[EmailStr] = Field("", description="test@email.com")
    MAIL_PORT: int = Field(587, description="server port")
    MAIL_SERVER: str = Field(None, description="mail server")
    MAIL_FROM_NAME: str = Field(None, description="Desired Sender Name")
    MAIL_STARTTLS: Optional[bool] = Field(True)
    MAIL_SSL_TLS: Optional[bool] = Field(False)
    USE_CREDENTIALS: Optional[bool] = Field(True)
    VALIDATE_CERTS: Optional[bool] = Field(True)
    TEMPLATE_FOLDER: Optional[str] = Field(None)


class SendEmailRequest(BaseModel):
    config: EmailConfig
    recipients: List[EmailStr]
    subject: str
    body: str
    body_type: Literal["html", "plain"]


class SendEmailResponse(BaseModel):
    message: str
    code: Optional[int]
