"""Registration and login rules. Knows nothing about HTTP or MongoDB."""
import logging
from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserLogin, UserRegister

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    async def register(self, payload: UserRegister) -> User:
        email = payload.email.lower()
        if await self._repository.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError()
        try:
            user = await self._repository.add(
                {
                    "email": email,
                    "name": payload.name,
                    "password_hash": hash_password(payload.password),
                    "created_at": datetime.now(timezone.utc),
                }
            )
        except DuplicateKeyError:
            # Two registrations raced; the unique index caught the second one.
            raise EmailAlreadyRegisteredError()
        logger.info("Registered user %s", user.id)
        return user

    async def login(self, payload: UserLogin) -> User:
        user = await self._repository.get_by_email(payload.email.lower())
        # Same error for unknown email and wrong password, so attackers
        # cannot discover which emails are registered.
        if user is None or not verify_password(payload.password, user.password_hash):
            logger.info("Failed login attempt")
            raise InvalidCredentialsError()
        logger.info("User %s logged in", user.id)
        return user

    @staticmethod
    def issue_token(user: User) -> str:
        return create_access_token(user.id)
