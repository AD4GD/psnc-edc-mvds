from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from api.models.db.registration_request import RegistrationStatus
from pydantic import AnyHttpUrl, BaseModel, Field, JsonValue, field_validator
import json
import ast

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
    created_at: Optional[datetime] = Field(...)
    updated_at: Optional[datetime] = Field(...)


class ConnectorResponse(BaseModel):
    id: str
    did: str
    protocol_url: AnyHttpUrl
    name: Optional[str] = None
    created_at: Optional[datetime] = Field(...)
    updated_at: Optional[datetime] = Field(...)


class ParticipantResponse(BaseModel):
    """Response model for participant information."""
    id: str
    name: str
    full_name: str
    VAT_number: str
    email: str
    location_id: str
    location: LocationResponse

    created_at: Optional[datetime] = Field(...)
    updated_at: Optional[datetime] = Field(...)

    data_space_components: dict[str, Any]

    @field_validator("data_space_components", mode="before")
    @classmethod
    def parse_components(cls, v):
        # Already a dict -> ok
        if isinstance(v, dict):
            return v

        # If it is a string, try JSON first, then python-literal dict
        if isinstance(v, str):
            s = v.strip()

            # 1) Try proper JSON
            try:
                return json.loads(s)
            except Exception:
                pass

            # 2) Try python dict literal string: "{'a': 1}"
            try:
                parsed = ast.literal_eval(s)
            except Exception as e:
                raise ValueError(f"data_space_components is not valid JSON or python dict literal: {e}")

            if not isinstance(parsed, dict):
                raise ValueError("data_space_components must be an object/dict")

            return parsed

        raise ValueError("data_space_components must be dict or string")

class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Literal["UP", "DOWN"]
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class VCResponse(BaseModel):
    """Response model for VC generating"""

    vc: Dict[str, Any] = Field(..., description="Verifiable Credential issued to the user")
    type: Literal["membership", "dataprocessor"] = Field(..., description="Type of the Verifiable Credential")
    connector_token: str = Field(..., description="Token that is used by participant to check integration")


class DIDResponse(BaseModel):
    """Response model for DID document."""

    service: List[Any]
    verificationMethod: List[Dict[str, Any]]
    authentication: List[str]
    id: str
    context: List[Any] = Field(alias="@context")


class RegistrationRequestResponse(BaseModel):
    id: UUID = Field(..., description="id")
    error_detail: str = Field("")
    status: RegistrationStatus = Field(RegistrationStatus.REQUESTED, description="current status of registration")
    email_confirmed: bool = Field(False, description="is email confirmed")
    created_at: Optional[datetime] = Field(..., description="")
    updated_at: Optional[datetime] = Field(..., description="")
