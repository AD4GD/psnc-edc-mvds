from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from api.core.database import AsyncSessionLocal
from api.core.logging_config import setup_logging
from api.models.db import RegistrationRequest
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError

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
                logger.error("Failed to create registration_request")
                raise

    async def get_registration_request(self, reg_id) -> Optional[RegistrationRequest]:
        """Get registration request by id."""
        async with self.session_factory() as session:
            return await session.get(RegistrationRequest, reg_id)
    
    async def confirm_email(self, reg_id: int) -> bool:
        async with self.session_factory() as session:
            obj = await session.get(RegistrationRequest, reg_id)
            if not obj:
                return False

            obj.email_confirmed = True
            await session.commit()
            return await session.refresh(obj)

    async def list_registration_requests(self, offset: int = 0, limit: int | None = None) -> List[RegistrationRequest]:
        """List registration requests, optional filter by participant."""
        async with self.session_factory() as session:
            stmt = select(RegistrationRequest)
            stmt = stmt.offset(offset).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_registration_requests_count(self) -> int:
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


async_postgres_service = AsyncPostgresService()
