"""Test doubles that stand in for the MongoDB repository."""
import uuid
from typing import Any, Dict, List, Optional

from pymongo.errors import ServerSelectionTimeoutError

from app.models.post import Post
from app.repositories.post_repository import PostRepository


class InMemoryPostRepository(PostRepository):
    def __init__(self):
        self._posts: Dict[str, Post] = {}

    async def add(self, data: Dict[str, Any]) -> Post:
        post = Post(id=uuid.uuid4().hex, **data)
        self._posts[post.id] = post
        return post

    async def list(self, skip: int, limit: int) -> List[Post]:
        newest_first = sorted(self._posts.values(), key=lambda p: p.created_at, reverse=True)
        return newest_first[skip : skip + limit]

    async def count(self) -> int:
        return len(self._posts)

    async def get(self, post_id: str) -> Optional[Post]:
        return self._posts.get(post_id)

    async def update(self, post_id: str, data: Dict[str, Any]) -> Optional[Post]:
        existing = self._posts.get(post_id)
        if existing is None:
            return None
        updated = existing.model_copy(update=data)
        self._posts[post_id] = updated
        return updated

    async def delete(self, post_id: str) -> bool:
        return self._posts.pop(post_id, None) is not None


class UnavailableDatabaseRepository(InMemoryPostRepository):
    """Simulates MongoDB being unreachable."""

    async def list(self, skip: int, limit: int) -> List[Post]:
        raise ServerSelectionTimeoutError("connection refused")
