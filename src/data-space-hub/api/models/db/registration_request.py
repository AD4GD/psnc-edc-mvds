from enum import Enum as PyEnum
from uuid import uuid4

from api.core.database import Base
from sqlalchemy import JSON, TIMESTAMP, Boolean, Column
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Text, text
from sqlalchemy.dialects.postgresql import UUID


class RegistrationStatus(PyEnum):
    REQUESTED = "REQUESTED"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    ONBOARDED = "ONBOARDED"  # approved & everything done


class RegistrationRequest(Base):
    __tablename__ = "registration_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    error_detail = Column(Text, nullable=True)
    status = Column(SAEnum(RegistrationStatus), nullable=False)
    request_form = Column(
        JSON, nullable=True
    )  # JSON string with request form, type-cheked with ParticipantCreateRequest
    email_confirmed = Column(Boolean, nullable=False, default=False)

    created_at = Column(TIMESTAMP(timezone=True), default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), default=text("now()"), onupdate=text("now()"))
