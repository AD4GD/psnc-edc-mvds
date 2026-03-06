from datetime import datetime

from api.core.database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RegistrationToken(Base):
    __tablename__ = "registration_token"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    request_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("registration_request.id", ondelete="CASCADE"),
        nullable=False,
        unique=False,
        index=False,
    )
    token: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    created_at: Mapped[datetime] = Column(TIMESTAMP(timezone=True), default=text("now()"))

    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        index=True,
    )

    # Null until token is used
    consumed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        index=True,
    )

    request = relationship("RegistrationRequest")
