from typing import Any, Dict, TypedDict
from uuid import uuid4

from api.core.database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ConnectorDict(TypedDict):
    id: str
    did: str
    name: str
    protocol_url: str
    participant_id: str
    participant: Dict[str, Any]
    # location_id: str
    # location: Dict[str, Any]
    created_at: int
    updated_at: int


class Connector(Base):
    __tablename__ = "connector"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    did = Column(String(255), nullable=False, unique=True)  # connector DID
    name = Column(String(255), nullable=False)  # connector name of participant
    protocol_url = Column(String, nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False)
    participant = relationship("Participant", back_populates="connectors", lazy="subquery")
    # location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"), nullable=True)
    # location = relationship("Location", lazy="subquery")

    created_at = Column(TIMESTAMP(timezone=True), default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), default=text("now()"), onupdate=text("now()"))

    def to_dict(self) -> ConnectorDict:
        return {
            "id": f"{str(self.id)}",
            "did": f"{self.did}",
            "name": f"{self.name}",
            "protocol_url": self.protocol_url,
            "participant_id": f"{self.participant_id}",
            "participant": self.participant.to_dict(),
            # "location_id": f"{self.location_id}",
            # "location": self.location.to_dict(),
            "created_at": f"{self.created_at}",
            "updated_at": f"{self.updated_at}",
        }
