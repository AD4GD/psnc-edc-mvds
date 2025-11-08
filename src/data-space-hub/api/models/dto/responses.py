from typing import Any, Dict, Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, Field

from .requests import UserRegistrationForm


class SimpleMessageResponse(BaseModel):
    """Response model for simple messages."""

    message: str


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str
    detail: Optional[str] = None


class LocationResponse(BaseModel):
    """Response model for location"""

    id: str
    country: str  # ISO_CODE 3166
    city: str
    postal_code: str
    street: str
    building_number: str


class ParticipantResponse(BaseModel):
    """Response model for participant information."""

    id: str
    did: str
    name: str
    full_name: str
    email: str
    protocol_url: AnyHttpUrl
    created_at: Optional[str]
    VAT_number: str
    location: LocationResponse


class UserRegistrationResponse(BaseModel):
    """Response model for user registration."""

    registration_form: UserRegistrationForm
    connector_token: str
    user_claims: Dict[str, Any]
    vc: Dict[str, Any] = Field(..., description="Verifiable Credential issued to the user")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Literal["UP", "DOWN"]
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
