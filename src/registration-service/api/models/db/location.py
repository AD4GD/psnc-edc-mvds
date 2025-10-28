from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from api.core.database import Base

class Location(Base):
    __tablename__ = 'location'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    country = Column(String(2), nullable=True) # ISO_CODE 3166 alpha_2 - pycountry
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    street = Column(String(200), nullable=True)
    building_number = Column(String(20), nullable=True)
    
    created_at = Column(TIMESTAMP(timezone=True), default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), default=text('now()'), onupdate=text('now()'))
