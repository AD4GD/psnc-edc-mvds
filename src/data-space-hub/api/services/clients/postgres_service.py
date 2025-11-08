from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from api.core.database import AsyncSessionLocal
from api.core.logging_config import setup_logging
from api.models.db import IssuedCredentials, Location, Participant, RegistrationRequest
from sqlalchemy import delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select

logger = setup_logging()


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
            except Exception:
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
            except Exception:
                await session.rollback()
                logger.exception("Failed to update participant")
                raise

    async def delete_participant(self, id: str = None, did: str = None) -> bool:
        """Delete participant by id or did. Returns True if deleted."""
        async with self.session_factory() as session:
            try:
                if id:
                    await session.execute(delete(Participant).where(Participant.id == id))
                elif did:
                    await session.execute(delete(Participant).where(Participant.did == did))
                else:
                    logger.info(f"Participant {id if id else did if did else None} not found during delete trial")
                    return False
                await session.commit()
                logger.info(f"Participant {id if id else did if did else None} was successfully deleted")
                return True
            except Exception:
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
            except Exception:
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
                await session.execute(update(Location).where(Location.id == location_id).values(**{**fields}))
                await session.commit()
                return await session.get(Location, location_id)
            except Exception:
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
            except Exception:
                await session.rollback()
                logger.exception("Failed to delete location")
                return False

    # --- RegistrationRequest / IssuedCredential helpers ---
    async def create_registration_request(self, data: Dict[str, Any]) -> RegistrationRequest:
        """Create a registration request audit row."""
        print(data)
        async with self.session_factory() as session:
            req = RegistrationRequest(**data)
            session.add(req)
            try:
                await session.commit()
                await session.refresh(req)
                return req
            except Exception:
                await session.rollback()
                logger.exception("Failed to create registration_request")
                raise

    async def get_registration_request(self, req_id) -> Optional[RegistrationRequest]:
        """Get registration request by id."""
        async with self.session_factory() as session:
            return await session.get(RegistrationRequest, req_id)

    async def list_registration_requests(self, skip: int = 0, limit: int = 50) -> List[RegistrationRequest]:
        """List registration requests, optional filter by participant."""
        async with self.session_factory() as session:
            stmt = select(RegistrationRequest)
            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_registration_request(self, req_id, fields: Dict[str, Any]) -> Optional[RegistrationRequest]:
        """Partial update of registration_request fields."""
        async with self.session_factory() as session:
            try:
                await session.execute(
                    update(RegistrationRequest)
                    .where(RegistrationRequest.id == req_id)
                    .values(**{**fields, "updated_at": datetime.now(timezone.utc)})
                )
                await session.commit()
                return await session.get(RegistrationRequest, req_id)
            except Exception:
                await session.rollback()
                logger.exception("Failed to update registration_request")
                raise

    async def delete_registration_request(self, req_id) -> bool:
        """Delete registration_request by id (cleanup on failure)."""
        async with self.session_factory() as session:
            try:
                await session.execute(delete(RegistrationRequest).where(RegistrationRequest.id == req_id))
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                logger.exception("Failed to delete registration_request")
                return False

    async def create_issued_credential(self, data: Dict[str, Any]) -> IssuedCredentials:
        """Create issued_credential row (status pending/active)."""
        async with self.session_factory() as session:
            ic = IssuedCredentials(**data, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
            session.add(ic)
            try:
                await session.commit()
                await session.refresh(ic)
                return ic
            except Exception:
                await session.rollback()
                logger.exception("Failed to create issued_credential")
                raise

    async def get_issued_credential(self, issued_id) -> Optional[IssuedCredentials]:
        """Get issued credential by id."""
        async with self.session_factory() as session:
            return await session.get(IssuedCredentials, issued_id)

    async def list_issued_credentials(
        self, participant_id: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> List[IssuedCredentials]:
        """List issued credentials with optional filters."""
        async with self.session_factory() as session:
            stmt = select(IssuedCredentials)
            if participant_id:
                stmt = stmt.where(IssuedCredentials.participant_id == participant_id)
            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_issued_credential(self, issued_id, fields: Dict[str, Any]) -> Optional[IssuedCredentials]:
        """Update issued credential fields (partial)."""
        async with self.session_factory() as session:
            try:
                await session.execute(
                    update(IssuedCredentials)
                    .where(IssuedCredentials.id == issued_id)
                    .values(**{**fields, "updated_at": datetime.now(timezone.utc)})
                )
                await session.commit()
                return await session.get(IssuedCredentials, issued_id)
            except Exception:
                await session.rollback()
                logger.exception("Failed to update issued_credential")
                raise

    async def delete_issued_credential(self, issued_id) -> bool:
        """Delete issued credential by id (used for cleanup on failure)."""
        async with self.session_factory() as session:
            try:
                await session.execute(delete(IssuedCredentials).where(IssuedCredentials.id == issued_id))
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                logger.exception("Failed to delete issued_credential")
                return False


async_postgres_service = AsyncPostgresService()
