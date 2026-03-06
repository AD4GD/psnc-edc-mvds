from datetime import datetime
from typing import Any, Dict, Literal, Optional
from uuid import UUID

from api.models.db.registration_request import RegistrationStatus
from pydantic import AnyHttpUrl, BaseModel, Field


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
    created_at: Optional[datetime] = Field(...)
    updated_at: Optional[datetime] = Field(...)
    VAT_number: str
    location: LocationResponse


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Literal["UP", "DOWN"]
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class VCResponse(BaseModel):
    """Response model for VC generating"""

    username: str
    vc: Dict[str, Any] = Field(..., description="Verifiable Credential issued to the user")
    connector_token: str = Field(..., description="Token that is used by participant to check integration")


class RegistrationRequestResponse(BaseModel):
    id: UUID = Field(..., description="id")
    error_detail: Optional[str] = Field("")
    status: RegistrationStatus = Field(RegistrationStatus.REQUESTED, description="current status of registration")
    email_confirmed: bool = Field(False, description="is email confirmed")
    created_at: Optional[datetime] = Field(..., description="")
    updated_at: Optional[datetime] = Field(..., description="")
