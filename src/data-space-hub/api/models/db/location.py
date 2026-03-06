from typing import TypedDict
from uuid import uuid4

from api.core.database import Base
from sqlalchemy import TIMESTAMP, Column, String, text
from sqlalchemy.dialects.postgresql import UUID


class LocationDict(TypedDict):
    id: str
    country: str
    city: str
    postal_code: str
    street: str
    building_number: str
    created_at: int
    updated_at: int


class Location(Base):
    __tablename__ = "location"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    country = Column(String(2), nullable=True)  # ISO_CODE 3166 alpha_2 - pycountry
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    street = Column(String(200), nullable=True)
    building_number = Column(String(20), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), default=text("now()"), onupdate=text("now()"))

    def to_dict(self) -> LocationDict:
        return {
            "id": f"{str(self.id)}",
            "country": f"{self.country}",
            "city": f"{self.city}",
            "postal_code": f"{self.postal_code}",
            "street": f"{self.street}",
            "building_number": f"{self.building_number}",
            "created_at": f"{self.created_at}",
            "updated_at": f"{self.updated_at}",
        }
