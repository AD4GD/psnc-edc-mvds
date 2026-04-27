from enum import Enum as PyEnum
from uuid import uuid4

from api.core.database import Base
from sqlalchemy import JSON, TIMESTAMP, Column
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class CredentialStatus(PyEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class IssuedCredentials(Base):
    __tablename__ = "issued_credentials"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    participant_id = Column(UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False)
    participant = relationship("Participant")
    credential_type = Column(String, nullable=True)  # e.g. MembershipCredential, DataProcessorCredential
    credential_id = Column(UUID(as_uuid=True), nullable=False)  # ID inside VC
    credential_hash = Column(String, nullable=False)  # hash of the issued VC
    credential_storage_ref = Column(String, nullable=True)  # reference to where the VC is stored (connector, path inside Vault, ...)

    issued_at = Column(TIMESTAMP(timezone=True), default=text("now()"))
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(SAEnum(CredentialStatus), nullable=False, default=CredentialStatus.ACTIVE)  # TODO delete after e.g. 6 months
    credential_metadata = Column(JSON, nullable=True)  # JSON string with additional metadata

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "participant_id": str(self.participant_id),
            "credential_type": self.credential_type,
            "credential_id": str(self.credential_id),
            "credential_hash": self.credential_hash,
            "credential_storage_ref": self.credential_storage_ref,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value if self.status else None,
            "credential_metadata": self.credential_metadata,
        }
