"""Business logic for posts. Knows nothing about HTTP or MongoDB."""
import logging
from datetime import datetime, timezone
from typing import Callable, List, Tuple

from app.core.exceptions import PostNotFoundError
from app.models.post import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreate, PostUpdate

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PostService:
    def __init__(self, repository: PostRepository, clock: Callable[[], datetime] = utc_now):
        self._repository = repository
        self._clock = clock

    async def create_post(self, payload: PostCreate) -> Post:
        now = self._clock()
        post = await self._repository.add(
            {**payload.model_dump(), "created_at": now, "updated_at": now}
        )
        logger.info("Created post %s", post.id)
        return post

    async def list_posts(self, skip: int, limit: int) -> Tuple[List[Post], int]:
        posts = await self._repository.list(skip=skip, limit=limit)
        total = await self._repository.count()
        return posts, total

    async def get_post(self, post_id: str) -> Post:
        post = await self._repository.get(post_id)
        if post is None:
            raise PostNotFoundError(post_id)
        return post

    async def update_post(self, post_id: str, payload: PostUpdate) -> Post:
        post = await self._repository.update(
            post_id, {**payload.model_dump(), "updated_at": self._clock()}
        )
        if post is None:
            raise PostNotFoundError(post_id)
        logger.info("Updated post %s", post_id)
        return post

    async def delete_post(self, post_id: str) -> None:
        if not await self._repository.delete(post_id):
            raise PostNotFoundError(post_id)
        logger.info("Deleted post %s", post_id)
