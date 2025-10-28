from sqlalchemy import Column, Text, TIMESTAMP, text, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from api.core.database import Base

class Participant(Base):
    __tablename__ = 'participant'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    did = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False) # nickname or shorten organization name
    full_name = Column(String(500), nullable=False) # full name of the organization
    VAT_number = Column(String(50), nullable=False) # VAT number if applicable
    protocol_url = Column(Text, nullable=False)
    email = Column(String(255), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey('location.id'), nullable=True)
    location = relationship('Location')

    created_at = Column(TIMESTAMP(timezone=True), default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), default=text('now()'), onupdate=text('now()'))
