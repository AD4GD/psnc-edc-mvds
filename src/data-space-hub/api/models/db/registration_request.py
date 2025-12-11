from __future__ import annotations

from enum import Enum as PyEnum
from typing import TypedDict
from uuid import uuid4

from api.core.database import Base
from api.models.dto.requests import ParticipantCreateRequest
from sqlalchemy import JSON, TIMESTAMP, Boolean, Column
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Text, text
from sqlalchemy.dialects.postgresql import UUID


class RegistrationStatus(PyEnum):
    REQUESTED = "REQUESTED"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    ONBOARDED = "ONBOARDED"  # approved & everything done

    @classmethod
    def normalize(cls, status: str | "RegistrationStatus") -> str:
        if isinstance(status, cls):
            return status.value
        if isinstance(status, str):
            return status.upper()
        raise TypeError(f"Unsupported status type: {type(status)}")

    @classmethod
    def __includes__(cls, status: str | "RegistrationStatus") -> bool:
        try:
            normalized = cls.normalize(status)
        except TypeError:
            return False
        return normalized in cls.__members__

    @classmethod
    def allowed_transitions(cls, current_status: str | "RegistrationStatus") -> list["RegistrationStatus"]:
        current = cls.normalize(current_status)
        transitions: dict[str, list["RegistrationStatus"]] = {
            "REQUESTED": [cls.APPROVED, cls.REJECTED],
            "APPROVED": [cls.ONBOARDED],
            "REJECTED": [],
            "ONBOARDED": [],
        }
        return transitions.get(current, [])

    @classmethod
    def can_transition(cls, current_status: str | "RegistrationStatus", new_status: str | "RegistrationStatus") -> bool:
        try:
            target = new_status if isinstance(new_status, cls) else cls(cls.normalize(new_status))
        except (ValueError, TypeError):
            return False
        return target in cls.allowed_transitions(current_status)


class RegistrationDict(TypedDict):
    id: str
    error_detail: str
    status: RegistrationStatus
    request_form: ParticipantCreateRequest
    email_confirmed: bool
    created_at: int
    updated_at: int


class RegistrationRequest(Base):
    __tablename__ = "registration_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    error_detail = Column(Text, nullable=True)
    status = Column(SAEnum(RegistrationStatus), nullable=False)
    request_form = Column(JSON, nullable=True)  # JSON string with request form, type-cheked with ParticipantCreateRequest
    email_confirmed = Column(Boolean, nullable=False, default=False)

    created_at = Column(TIMESTAMP(timezone=True), default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), default=text("now()"), onupdate=text("now()"))

    def to_dict(self) -> RegistrationDict:
        return {
            "id": f"{self.id}",
            "error_detail": f"{self.error_detail}",
            "status": f"{self.status}",
            "request_form": f"{self.request_form}",
            "email_confirmed": f"{self.email_confirmed}",
            "created_at": f"{self.created_at}",
            "updated_at": f"{self.updated_at}",
        }
