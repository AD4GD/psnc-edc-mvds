import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from api.core.logging_config import setup_logging
from api.services.infrastructure.registration_token_repository import registration_token_repository
from sqlalchemy.dialects.postgresql import UUID

logger = setup_logging()


class RegistrationTokenService:
    """Service responsible for issuing and validation registration tokens."""

    def __init__(self):
        pass

    async def generate_token(self, request_id: UUID) -> str:
        token = secrets.token_urlsafe(32)
        _hash = sha256(token.encode("utf-8")).hexdigest()

        await self._save_token(request_id, _hash)

        return _hash

    @classmethod
    async def _save_token(cls, request_id: UUID, token: str):
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        return await registration_token_repository.create(request_id, token, expires_at)

    @classmethod
    async def is_valid_token(cls, request_id: UUID, token: str):
        token_entry = await registration_token_repository.get(request_id, token)
        logger.info(token_entry)
        logger.info(f"{request_id}#{token}")

        if token_entry is None:
            return False

        if token_entry.expires_at < datetime.now(timezone.utc):
            return False

        if token_entry.consumed_at is not None:
            return False

        return True

    @classmethod
    async def consume_token(cls, request_id: UUID, token: str):
        token_entry = await registration_token_repository.get(request_id, token)
        token_entry.consumed_at = datetime.now(timezone.utc)
        return await registration_token_repository.update(token_entry)


registration_token_service = RegistrationTokenService()
