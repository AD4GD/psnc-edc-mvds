import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select
from sqlalchemy import update, delete

from api.core.database import AsyncSessionLocal
from api.models.db.location import Location
from api.models.db.participant import Participant

logger = logging.getLogger(__name__)

class AsyncPostgresService:
    """Asynchronous service for interacting with PostgreSQL database."""

    def __init__(self):
        self.session_factory = AsyncSessionLocal

    async def health(self) -> bool:
        """Check database connectivity."""
        try:
            async with self.session_factory() as session:
                await session.execute(select(1))
            return True
        except SQLAlchemyError as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False

    # --- Participant helpers ---
    async def create_participant(self, participant_data: Dict[str, Any]) -> Participant:
        """Insert new participant record (participant_data is a dict)."""
        async with self.session_factory() as session:
            participant = Participant(**participant_data)
            session.add(participant)
            try:
                await session.commit()
                await session.refresh(participant)
                return participant
            except Exception as e:
                await session.rollback()
                logger.exception("Failed to create participant")
                raise

    async def get_participant(self, participant_id) -> Optional[Participant]:
        """Get participant by ID."""
        async with self.session_factory() as session:
            return await session.get(Participant, participant_id)

    async def get_participant_by_did(self, did: str) -> Optional[Participant]:
        """Get participant by DID (unique)."""
        async with self.session_factory() as session:
            result = await session.execute(select(Participant).where(Participant.did == did))
            return result.scalars().first()

    async def list_participants(self, skip: int = 0, limit: int = 10) -> List[Participant]:
        """Fetch paginated list of participants."""
        async with self.session_factory() as session:
            result = await session.execute(select(Participant).offset(skip).limit(limit))
            return result.scalars().all()

    async def update_participant(self, participant_id, fields: Dict[str, Any]) -> Optional[Participant]:
        """Partial update of participant fields. Returns updated participant or None."""
        async with self.session_factory() as session:
            try:
                await session.execute(
                    update(Participant)
                    .where(Participant.id == participant_id)
                    .values(**{**fields, "updated_at": datetime.utcnow()})
                )
                await session.commit()
                return await session.get(Participant, participant_id)
            except Exception as e:
                await session.rollback()
                logger.exception("Failed to update participant")
                raise

    async def delete_participant(self, participant_id) -> bool:
        """Delete participant by id. Returns True if deleted."""
        async with self.session_factory() as session:
            try:
                await session.execute(delete(Participant).where(Participant.id == participant_id))
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logger.exception("Failed to delete participant")
                return False

    # --- Location helpers ---
    async def create_location(self, location_data: Dict[str, Any]) -> Location:
        """Insert new location record."""
        async with self.session_factory() as session:
            loc = Location(**location_data)
            session.add(loc)
            try:
                await session.commit()
                await session.refresh(loc)
                return loc
            except Exception as e:
                await session.rollback()
                logger.exception("Failed to create location")
                raise

    async def get_location(self, location_id) -> Optional[Location]:
        """Get location by ID."""
        async with self.session_factory() as session:
            return await session.get(Location, location_id)

    async def update_location(self, location_id, fields: Dict[str, Any]) -> Optional[Location]:
        """Partial update of location fields."""
        async with self.session_factory() as session:
            try:
                await session.execute(
                    update(Location)
                    .where(Location.id == location_id)
                    .values(**{**fields})
                )
                await session.commit()
                return await session.get(Location, location_id)
            except Exception as e:
                await session.rollback()
                logger.exception("Failed to update location")
                raise

    async def delete_location(self, location_id) -> bool:
        """Delete location by id."""
        async with self.session_factory() as session:
            try:
                await session.execute(delete(Location).where(Location.id == location_id))
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logger.exception("Failed to delete location")
                return False

async_postgres_service = AsyncPostgresService()
