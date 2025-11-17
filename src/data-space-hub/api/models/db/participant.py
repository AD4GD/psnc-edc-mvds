from typing import Any, Dict, TypedDict
from uuid import uuid4

from api.core.database import Base
from sqlalchemy import ARRAY, TIMESTAMP, Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ParticipantDict(TypedDict):
    id: str
    did: str
    name: str
    full_name: str
    VAT_number: str
    protocol_url: str
    email: str
    location_id: str
    location: Dict[str, Any]
    created_at: int
    updated_at: int


class Participant(Base):
    __tablename__ = "participant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    did = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)  # nickname or shorten organization name
    full_name = Column(String(500), nullable=False)  # full name of the organization
    VAT_number = Column(String(50), nullable=False)  # VAT number if applicable
    protocol_url = Column(ARRAY(String), nullable=False)
    ums_url = Column(String, nullable=False)
    email = Column(String(255), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"), nullable=True)
    location = relationship("Location", lazy="subquery")

    created_at = Column(TIMESTAMP(timezone=True), default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), default=text("now()"), onupdate=text("now()"))

    def __info_to_json__(self) -> ParticipantDict:
        return {
            "id": f"{self.id}",
            "did": f"{self.did}",
            "name": f"{self.name}",
            "full_name": f"{self.full_name}",
            "VAT_number": f"{self.VAT_number}",
            "protocol_url": f"{self.protocol_url}",
            "email": f"{self.email}",
            "location_id": f"{self.location_id}",
            "location": {self.location.__info_to_json__()},
            "created_at": f"{self.created_at}",
            "updated_at": f"{self.updated_at}",
        }
