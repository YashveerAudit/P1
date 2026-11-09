"""Data access for posts.

`PostRepository` is the abstraction the service layer depends on
(Dependency Inversion). `MongoPostRepository` is the production
implementation; tests use an in-memory one, so no database is needed.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import DESCENDING, ReturnDocument
from pymongo.asynchronous.collection import AsyncCollection

from app.models.post import Post


class PostRepository(ABC):
    @abstractmethod
    async def add(self, data: Dict[str, Any]) -> Post: ...

    @abstractmethod
    async def list(self, skip: int, limit: int) -> List[Post]:
        """Return posts, newest first."""

    @abstractmethod
    async def count(self) -> int: ...

    @abstractmethod
    async def get(self, post_id: str) -> Optional[Post]: ...

    @abstractmethod
    async def update(self, post_id: str, data: Dict[str, Any]) -> Optional[Post]: ...

    @abstractmethod
    async def delete(self, post_id: str) -> bool:
        """Return True if a post was deleted, False if it did not exist."""


def _parse_object_id(post_id: str) -> Optional[ObjectId]:
    try:
        return ObjectId(post_id)
    except (InvalidId, TypeError):
        return None


_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _to_post(doc: Dict[str, Any]) -> Post:
    raw_id = doc["_id"]
    # Legacy posts created before timestamps existed fall back to the
    # ObjectId's creation time (or the epoch if the id isn't an ObjectId).
    created_at = doc.get("created_at") or (
        raw_id.generation_time if isinstance(raw_id, ObjectId) else _EPOCH
    )
    return Post(
        id=str(raw_id),
        title=doc["title"],
        content=doc["content"],
        author=doc["author"],
        created_at=created_at,
        updated_at=doc.get("updated_at") or created_at,
    )


class MongoPostRepository(PostRepository):
    def __init__(self, collection: AsyncCollection):
        self._collection = collection

    async def add(self, data: Dict[str, Any]) -> Post:
        document = dict(data)
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return _to_post(document)

    async def list(self, skip: int, limit: int) -> List[Post]:
        cursor = (
            self._collection.find()
            .sort([("created_at", DESCENDING), ("_id", DESCENDING)])
            .skip(skip)
            .limit(limit)
        )
        return [_to_post(doc) async for doc in cursor]

    async def count(self) -> int:
        return await self._collection.count_documents({})

    async def get(self, post_id: str) -> Optional[Post]:
        object_id = _parse_object_id(post_id)
        if object_id is None:
            return None
        doc = await self._collection.find_one({"_id": object_id})
        return _to_post(doc) if doc else None

    async def update(self, post_id: str, data: Dict[str, Any]) -> Optional[Post]:
        object_id = _parse_object_id(post_id)
        if object_id is None:
            return None
        doc = await self._collection.find_one_and_update(
            {"_id": object_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return _to_post(doc) if doc else None

    async def delete(self, post_id: str) -> bool:
        object_id = _parse_object_id(post_id)
        if object_id is None:
            return False
        result = await self._collection.delete_one({"_id": object_id})
        return result.deleted_count == 1
