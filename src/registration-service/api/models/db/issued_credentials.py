from sqlalchemy import Column, String, TIMESTAMP, text, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from enum import Enum as PyEnum
from api.core.database import Base


class CredentialStatus(PyEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class IssuedCredentials(Base):
    __tablename__ = 'issued_credentials'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())

    participant_id = Column(UUID(as_uuid=True), ForeignKey('participant.id'), nullable=False)
    participant = relationship('Participant')
    username = Column(String, nullable=False)  # username of the user to whom the VC was issued
    credential_id = Column(UUID(as_uuid=True), nullable=False)  # ID inside VC
    credential_hash = Column(String, nullable=False)  # hash of the issued VC
    credential_storage_ref = Column(String, nullable=True)  # reference to where the VC is stored (connector, path inside Vault, ...)

    issued_at = Column(TIMESTAMP(timezone=True), default=text('now()'))
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(SAEnum(CredentialStatus), nullable=False, default=CredentialStatus.ACTIVE)  # active, revoked, expired TODO Enum
    credential_metadata = Column(JSON, nullable=True)  # JSON string with additional metadata
