"""Test doubles that stand in for the MongoDB repositories."""
import uuid
from typing import Any, Dict, List, Optional

from pymongo.errors import ServerSelectionTimeoutError

from app.models.post import Post
from app.models.user import User
from app.repositories.post_repository import PostRepository
from app.repositories.user_repository import UserRepository


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


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: Dict[str, User] = {}

    async def add(self, data: Dict[str, Any]) -> User:
        user = User(id=uuid.uuid4().hex, **data)
        self._users[user.id] = user
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._users.values() if u.email == email), None)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)
