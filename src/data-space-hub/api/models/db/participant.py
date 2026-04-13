from typing import Any, Dict, TypedDict
from uuid import uuid4

from api.core.database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ParticipantDict(TypedDict):
    id: str
    name: str
    full_name: str
    VAT_number: str
    data_space_components: JSON
    email: str
    keycloak_id: str
    location_id: str
    location: Dict[str, Any]
    created_at: int
    updated_at: int


class Participant(Base):
    __tablename__ = "participant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    name = Column(String(255), nullable=False)  # nickname or shorten organization name
    full_name = Column(String(500), nullable=False)  # full name of the organization
    VAT_number = Column(String(50), nullable=False)  # VAT number if applicable
    data_space_components = Column(JSON, nullable=True)
    email = Column(String(255), nullable=False)
    keycloak_id = Column(String(255), nullable=True, unique=True, index=True)  # Keycloak 'sub' (user UUID)
    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"), nullable=True)
    location = relationship("Location", lazy="subquery")

    created_at = Column(TIMESTAMP(timezone=True), default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), default=text("now()"), onupdate=text("now()"))

    def to_dict(self) -> ParticipantDict:
        return {
            "id": f"{str(self.id)}",
            "name": f"{self.name}",
            "full_name": f"{self.full_name}",
            "VAT_number": f"{self.VAT_number}",
            "data_space_components": f"{self.data_space_components}",
            "email": f"{self.email}",
            "keycloak_id": f"{self.keycloak_id}" if self.keycloak_id else None,
            "location_id": f"{self.location_id}",
            "location": self.location.to_dict(),
            "created_at": f"{self.created_at}",
            "updated_at": f"{self.updated_at}",
        }
