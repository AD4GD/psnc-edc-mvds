from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from api.core.database import Base

class Contact(Base):
    __tablename__ = 'contact'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    email = Column(String(255), nullable=False)
    phone_no = Column(String(25), nullable=True) # request in json E164 format
    
    created_at = Column(TIMESTAMP(timezone=True), default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), default=text('now()'), onupdate=text('now()'))
