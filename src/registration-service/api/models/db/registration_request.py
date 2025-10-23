from sqlalchemy import JSON, Column, Text, TIMESTAMP, text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from enum import Enum as PyEnum
from api.core.database import Base


class RegistrationStatus(PyEnum):
    REQUESTED = "requested"
    REJECTED = "rejected"
    APPROVED = "approved"
    ONBOARDED = "onboarded" # approved & everything done


class RegistrationRequest(Base):
    __tablename__ = 'registration_request'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    error_detail = Column(Text, nullable=True)
    status = Column(SAEnum(RegistrationStatus), nullable=False)
    request_form = Column(JSON, nullable=True)  # JSON string with request form, type-cheked with ParticipantCreateRequest

    created_at = Column(TIMESTAMP(timezone=True), default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), default=text('now()'), onupdate=text('now()'))
