from typing import Any, Dict, List, Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field


class LocationRequest(BaseModel):
    """Request model for creating or updating a location."""

    country: Optional[str] = Field(..., max_length=2)  # ISO_CODE 3166 alpha_2 - pycountry
    city: Optional[str] = Field(..., max_length=100)
    postal_code: Optional[str] = Field(..., max_length=20)
    street: str = Field(..., max_length=200)
    building_number: Optional[str] = Field(..., max_length=20)

class ConnectorRequest(BaseModel):
    did: str = Field(..., description="Participant DID")
    name: Optional[str] = Field(None, description="Participant connector name")
    protocol_url: AnyHttpUrl = Field(..., description="Participant connector protocol URL")

class InsertVcRequest(BaseModel):
    connector_did: str = Field(..., description="DID of participant owning the connector")
    connector_dsp_url: str = Field(..., description="Connector DSP protocol URL (for FC target node registration)")
    identity_hub_identity_url: str = Field(..., description="Identity Hub identity API URL")
    identity_hub_api_key: Optional[str] = Field(None, description="Identity Hub super-user API key (omit to skip IH push)")


class RegistrationCreateRequest(BaseModel):
    """Request model for public self-registration (company info only, no infra details)."""
    name: str = Field(..., description="Company short name")
    full_name: str = Field(..., description="Company full legal name")
    VAT_number: str = Field(..., description="Company VAT number")
    email: EmailStr = Field(..., description="Contact email for the registering employee")
    location: LocationRequest = Field(..., description="Company address")


class ParticipantCreateRequest(BaseModel):
    """Request model for creating a new participant."""
    name: str = Field(..., description="Participant name")
    full_name: str = Field(..., description="Participant full name")
    VAT_number: str = Field(..., description="Participant VAT number")
    email: EmailStr = Field(..., description="Participant contact email")
    location: LocationRequest = Field(None, description="Location info")
    data_space_components: InsertVcRequest = Field(..., description="Data Space Components")

class ParticipantUpdateRequest(BaseModel):
    id: str = Field(..., description="Participant UUID")
    identity_hub_url: AnyHttpUrl = Field(..., description="Participant connector protocol URL")
    name: str = Field(..., description="Participant name")
    full_name: str = Field(None, description="Participant full name")
    VAT_number: str = Field(None, description="Participant VAT number")
    email: EmailStr = Field(..., description="Participant contact email")
    location: LocationRequest = Field(None, description="Location info")
    connector: ConnectorRequest = Field(..., description="Participant connector info")


class GenerateVcRequest(BaseModel):
    """Request model for VC creation dedicated to single user."""
    connector_did: str = Field(..., description="DID of participant owning the connector")
    vc_format: str = Field(..., description="vc format")
    credential_type: Literal["MembershipCredential", "DataProcessorCredential"] = Field(..., description="credential type")