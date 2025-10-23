from pydantic import BaseModel, AnyHttpUrl, Field
from typing import Literal, Optional


class SimpleMessageResponse(BaseModel):
    """ Response model for simple messages. """

    message: str


class ErrorResponse(BaseModel):
    """ Response model for errors. """

    error: str
    detail: Optional[str] = None


class ParticipantResponse(BaseModel):
    """ Response model for participant information. """
    id: str
    did: str
    name: str
    protocol_url: AnyHttpUrl
    created_at: Optional[str]


class UserRegistrationResponse(BaseModel):
    """ Response model for user registration. """
    credential_id: str
    credential_hash: str
    issued_at: str
    issued_to: str
    storage_ref: Optional[str]


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Literal["UP", "DOWN"]
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")