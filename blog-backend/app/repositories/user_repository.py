"""Data access for users: an abstract interface plus the MongoDB implementation."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING
from pymongo.asynchronous.collection import AsyncCollection

from app.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def add(self, data: Dict[str, Any]) -> User: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]: ...


def _to_user(doc: Dict[str, Any]) -> User:
    return User(
        id=str(doc["_id"]),
        email=doc["email"],
        name=doc["name"],
        password_hash=doc["password_hash"],
        created_at=doc["created_at"],
    )


class MongoUserRepository(UserRepository):
    def __init__(self, collection: AsyncCollection):
        self._collection = collection

    @staticmethod
    async def ensure_indexes(collection: AsyncCollection) -> None:
        """Emails must be unique; enforced by the database, not just the code."""
        await collection.create_index([("email", ASCENDING)], unique=True)

    async def add(self, data: Dict[str, Any]) -> User:
        document = dict(data)
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return _to_user(document)

    async def get_by_email(self, email: str) -> Optional[User]:
        doc = await self._collection.find_one({"email": email})
        return _to_user(doc) if doc else None

    async def get_by_id(self, user_id: str) -> Optional[User]:
        try:
            object_id = ObjectId(user_id)
        except (InvalidId, TypeError):
            return None
        doc = await self._collection.find_one({"_id": object_id})
        return _to_user(doc) if doc else None
