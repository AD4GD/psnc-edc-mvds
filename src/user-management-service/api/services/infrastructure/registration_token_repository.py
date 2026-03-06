from datetime import datetime
from api.core.logging_config import setup_logging
from api.core.database import AsyncSessionLocal
from api.models.db import RegistrationToken
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select
from uuid import UUID

logger = setup_logging()

class RegistrationTokenRepository:

    def __init__(self):
        self.session_factory = AsyncSessionLocal

    async def create(self, request_id: UUID, token: str, expires_at: datetime) -> RegistrationToken:

        obj = RegistrationToken(request_id=request_id, token=token, expires_at = expires_at)

        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add(obj)
            return obj

        except IntegrityError as ex:
            logger.warning(
                "Failed to insert RegistrationToken (request_id=%s). Constraint violation.",
                request_id, exc_info=ex
            )
            raise
        except SQLAlchemyError as ex:
            logger.exception("DB error while creating RegistrationToken", exc_info=ex)
            raise

    async def get(self, request_id: UUID, token_hash: str) -> RegistrationToken | None:
        async with self.session_factory() as session:
            stmt = (
                select(RegistrationToken)
                .where(
                    RegistrationToken.request_id == request_id,
                    RegistrationToken.token == token_hash,
                    RegistrationToken.consumed_at == None
                )
                .limit(1)
            )

            # returns model instance or None
            return await session.scalar(stmt)
        
    async def update(self, token_entry: RegistrationToken) -> RegistrationToken:
        async with self.session_factory() as session:
            async with session.begin():
                session.add(token_entry)
            return token_entry

registration_token_repository = RegistrationTokenRepository()