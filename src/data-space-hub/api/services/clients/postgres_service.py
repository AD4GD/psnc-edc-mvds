from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

from api.core.database import AsyncSessionLocal
from api.core.logging_config import setup_logging
from api.models.db import Connector, IssuedCredentials, Location, Participant, RegistrationRequest
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = setup_logging()


class AsyncPostgresService:
    """Asynchronous service for interacting with PostgreSQL database."""

    def __init__(self):
        self.session_factory = AsyncSessionLocal

    @asynccontextmanager
    async def atomic(self) -> AsyncGenerator[AsyncSession, None]:
        """Zapewnia atomowość operacji w bloku."""
        async with self.session_factory() as session:
            async with session.begin():
                yield session

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
    async def create_participant(self, participant_data: Dict[str, Any], session: Optional[AsyncSession]) -> Participant:
        """Insert new participant record (participant_data is a dict)."""

        async def _create(sess: AsyncSession) -> Participant:
            participant = Participant(**participant_data)
            sess.add(participant)
            await sess.flush()  # Flush zamiast commit, żeby nie kończyć transakcji
            await sess.refresh(participant)
            return participant

        if session:
            return await _create(session)
        else:
            async with self.session_factory() as session_:
                participant = Participant(**participant_data)
                session_.add(participant)
                try:
                    await session_.commit()
                    await session_.refresh(participant)
                    return participant
                except Exception:  # pylint: disable=W0718
                    await session_.rollback()
                    logger.error("Failed to create participant")
                    return None

    async def get_participant(self, participant_id) -> Optional[Participant]:
        """Get participant by ID."""
        async with self.session_factory() as session:
            return await session.get(Participant, participant_id)

    async def get_participant_count(self) -> int:
        async with self.session_factory() as session:
            stmt = select(func.count()).select_from(Participant)
            result = await session.execute(stmt)
            count = result.scalar_one()
            return count or 0

    async def list_participants(self, offset: int = 0, limit: int | None = None) -> List[Participant]:
        """Fetch paginated list of participants."""
        async with self.session_factory() as session:
            result = await session.execute(select(Participant).offset(offset).limit(limit))
            return result.scalars().all()

    async def update_participant(self, participant_id, fields: Dict[str, Any]) -> Optional[Participant]:
        """Partial update of participant fields. Returns updated participant or None."""
        async with self.session_factory() as session:
            try:
                await session.execute(
                    update(Participant)
                    .where(Participant.id == participant_id)
                    .values(**{**fields, "updated_at": datetime.now(datetime.timezone.utc)})
                )
                await session.commit()
                return await session.get(Participant, participant_id)
            except Exception:  # pylint: disable=W0718
                await session.rollback()
                logger.error("Failed to update participant")
                return None

    async def delete_participant(self, p_id: str) -> bool:
        """Delete participant by id or did. Returns True if deleted."""
        async with self.session_factory() as session:
            try:
                await session.execute(delete(Participant).where(Participant.id == p_id))
                await session.commit()
                logger.info(f"Participant {p_id} was successfully deleted")
                return True
            except Exception:  # pylint: disable=W0718
                await session.rollback()
                logger.error("Failed to delete participant")
                return False

    # --- Email confirmation helpers ---
    async def confirm_email(self, reg_id: int) -> bool:
        async with self.session_factory() as session:
            obj = await session.get(RegistrationRequest, reg_id)
            if not obj:
                return False

            obj.email_confirmed = True
            await session.commit()
            return await session.refresh(obj)

    # --- Location helpers ---
    async def create_location(self, location_data: Dict[str, Any], session: Optional[AsyncSession] = None) -> Location:
        """Insert new location record. Optionally uses provided session (for transactions)."""

        async def _create(sess: AsyncSession) -> Location:
            loc = Location(**location_data)
            sess.add(loc)
            await sess.flush()
            await sess.refresh(loc)
            return loc

        if session:
            return await _create(session)
        else:
            async with self.session_factory() as sess:
                try:
                    result = await _create(sess)
                    await sess.commit()
                    return result
                except Exception:  # pylint: disable=W0718
                    await sess.rollback()
                    logger.error("Failed to create location")
                    return None

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
                logger.error("Failed to update location")
                raise

    async def delete_location(self, location_id) -> bool:
        """Delete location by id."""
        async with self.session_factory() as session:
            try:
                await session.execute(delete(Location).where(Location.id == location_id))
                await session.commit()
                return True
            except Exception:  # pylint: disable=W0718
                await session.rollback()
                logger.error("Failed to delete location")
                return False

    # --- Connector helpers ---
    async def create_connector(self, connector_data: Dict[str, Any], session: Optional[AsyncSession] = None) -> Connector:
        """Insert new connector record. Optionally uses provided session (for transactions)."""

        async def _create(sess: AsyncSession) -> Connector:
            conn = Connector(**connector_data)
            sess.add(conn)
            await sess.flush()
            await sess.refresh(conn)
            return conn

        if session:
            return await _create(session)
        else:
            async with self.session_factory() as sess:
                try:
                    result = await _create(sess)
                    await sess.commit()
                    return result
                except Exception:  # pylint: disable=W0718
                    await sess.rollback()
                    logger.error("Failed to create connector")
                    return None

    async def get_connector(self, connector_id) -> Optional[Connector]:
        """Get connector by ID."""
        async with self.session_factory() as session:
            return await session.get(Connector, connector_id)

    async def get_connector_by_did(self, did: str) -> Optional[Connector]:
        """Get connector by DID (unique)."""
        async with self.session_factory() as session:
            result = await session.execute(select(Connector).where(Connector.did == did))
            return result.scalars().first()

    async def list_connectors(self, offset: int = 0, limit: int | None = None) -> List[Connector]:
        """Fetch paginated list of connectors."""
        async with self.session_factory() as session:
            result = await session.execute(select(Connector).offset(offset).limit(limit))
            return result.scalars().all()

    async def get_connectors_count(self) -> int:
        async with self.session_factory() as session:
            stmt = select(func.count()).select_from(Connector)
            result = await session.execute(stmt)
            count = result.scalar_one()
            return count or 0

    async def get_connectors_count_by_participant(self, participant_id: str) -> int:
        async with self.session_factory() as session:
            stmt = select(func.count()).select_from(Connector).where(Connector.participant_id == participant_id)
            result = await session.execute(stmt)
            count = result.scalar_one()
            return count or 0

    async def list_connectors_by_participant(self, participant_id: str, offset: int = 0, limit: int | None = None) -> List[Connector]:
        """Fetch paginated list of connectors for a given participant."""
        async with self.session_factory() as session:
            stmt = select(Connector).where(Connector.participant_id == participant_id).offset(offset).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_connector(self, connector_id, fields: Dict[str, Any]) -> Optional[Connector]:
        """Partial update of connector fields."""
        async with self.session_factory() as session:
            try:
                await session.execute(update(Connector).where(Connector.id == connector_id).values(**{**fields}))
                await session.commit()
                return await session.get(Connector, connector_id)
            except Exception:
                await session.rollback()
                logger.error("Failed to update connector")
                raise

    async def delete_connector(self, connector_id) -> bool:
        """Delete connector by id."""
        async with self.session_factory() as session:
            try:
                await session.execute(delete(Connector).where(Connector.id == connector_id))
                await session.commit()
                return True
            except Exception:  # pylint: disable=W0718
                await session.rollback()
                logger.error("Failed to delete connector")
                return False

    # --- RegistrationRequest / IssuedCredential helpers ---
    async def create_registration_request(self, data: Dict[str, Any]) -> RegistrationRequest:
        """Create a registration request audit row."""
        async with self.session_factory() as session:
            req = RegistrationRequest(**data)
            session.add(req)
            try:
                await session.commit()
                await session.refresh(req)
                return req
            except Exception:
                await session.rollback()
                logger.error("Failed to create registration_request")
                raise

    async def get_registration_request(self, reg_id) -> Optional[RegistrationRequest]:
        """Get registration request by id."""
        async with self.session_factory() as session:
            return await session.get(RegistrationRequest, reg_id)

    async def list_registration_requests(self, offset: int = 0, limit: int | None = None) -> List[RegistrationRequest]:
        """List registration requests, optional filter by participant."""
        async with self.session_factory() as session:
            stmt = select(RegistrationRequest)
            stmt = stmt.offset(offset).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_registration_request_count(self) -> int:
        async with self.session_factory() as session:
            stmt = select(func.count()).select_from(RegistrationRequest)
            result = await session.execute(stmt)
            count = result.scalar_one()
            return count or 0

    async def update_registration_request(self, req_id, fields: Dict[str, Any]) -> Optional[RegistrationRequest]:
        """Partial update of registration_request fields."""
        async with self.session_factory() as session:
            try:
                await session.execute(
                    update(RegistrationRequest).where(RegistrationRequest.id == req_id).values(**{**fields, "updated_at": datetime.now(timezone.utc)})
                )
                await session.commit()
                return await session.get(RegistrationRequest, req_id)
            except Exception:
                await session.rollback()
                logger.error("Failed to update registration_request")
                raise

    async def delete_registration_request(self, req_id) -> bool:
        """Delete registration_request by id (cleanup on failure)."""
        async with self.session_factory() as session:
            try:
                outcome = await session.execute(delete(RegistrationRequest).where(RegistrationRequest.id == req_id))
                await session.commit()
                count = outcome.rowcount
                logger.info(f"Deleted {count} registration_request with id {req_id}")
                return count
            except Exception as ex:  # pylint: disable=W0718
                await session.rollback()
                logger.error(f"Failed to delete registration_request: {ex}")
                return 0

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
                logger.error("Failed to create issued_credential")
                raise

    async def get_issued_credential(self, issued_id) -> Optional[IssuedCredentials]:
        """Get issued credential by id."""
        async with self.session_factory() as session:
            return await session.get(IssuedCredentials, issued_id)

    async def list_issued_credentials(
        self, participant_id: Optional[str] = None, offset: int = 0, limit: int | None = None
    ) -> List[IssuedCredentials]:
        """List issued credentials with optional filters."""
        async with self.session_factory() as session:
            stmt = select(IssuedCredentials)
            if participant_id:
                stmt = stmt.where(IssuedCredentials.participant_id == participant_id)
            stmt = stmt.offset(offset).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_issued_credential(self, issued_id, fields: Dict[str, Any]) -> Optional[IssuedCredentials]:
        """Update issued credential fields (partial)."""
        async with self.session_factory() as session:
            try:
                await session.execute(
                    update(IssuedCredentials).where(IssuedCredentials.id == issued_id).values(**{**fields, "updated_at": datetime.now(timezone.utc)})
                )
                await session.commit()
                return await session.get(IssuedCredentials, issued_id)
            except Exception:
                await session.rollback()
                logger.error("Failed to update issued_credential")
                raise

    async def delete_issued_credential(self, issued_id) -> bool:
        """Delete issued credential by id (used for cleanup on failure)."""
        async with self.session_factory() as session:
            try:
                await session.execute(delete(IssuedCredentials).where(IssuedCredentials.id == issued_id))
                await session.commit()
                return True
            except Exception:  # pylint: disable=W0718
                await session.rollback()
                logger.error("Failed to delete issued_credential")
                return False


async_postgres_service = AsyncPostgresService()
