"""Unit tests for PostService business rules, independent of HTTP."""
from datetime import datetime, timedelta, timezone

import pytest

from app.core.exceptions import PostNotFoundError
from app.schemas.post import PostCreate, PostUpdate
from app.services.post_service import PostService
from tests.fakes import InMemoryPostRepository

pytestmark = pytest.mark.anyio


class FakeClock:
    """A controllable clock so timestamp behaviour can be asserted exactly."""

    def __init__(self):
        self.now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, minutes: int) -> None:
        self.now += timedelta(minutes=minutes)


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def service(clock):
    return PostService(InMemoryPostRepository(), clock=clock)


@pytest.fixture
def payload():
    return PostCreate(title="Hello world", content="Some content here.", author="Ana")


async def test_create_sets_both_timestamps_to_now(service, clock, payload):
    post = await service.create_post(payload)

    assert post.created_at == clock.now
    assert post.updated_at == clock.now


async def test_update_changes_updated_at_but_not_created_at(service, clock, payload):
    post = await service.create_post(payload)
    clock.advance(minutes=5)

    updated = await service.update_post(
        post.id, PostUpdate(title="New title", content=payload.content, author=payload.author)
    )

    assert updated.title == "New title"
    assert updated.created_at == post.created_at
    assert updated.updated_at == post.created_at + timedelta(minutes=5)


async def test_get_missing_post_raises_not_found(service):
    with pytest.raises(PostNotFoundError):
        await service.get_post("missing")


async def test_update_missing_post_raises_not_found(service, payload):
    with pytest.raises(PostNotFoundError):
        await service.update_post("missing", PostUpdate(**payload.model_dump()))


async def test_delete_missing_post_raises_not_found(service):
    with pytest.raises(PostNotFoundError):
        await service.delete_post("missing")


async def test_list_returns_total_count_independent_of_page_size(service, clock, payload):
    for _ in range(3):
        await service.create_post(payload)
        clock.advance(minutes=1)

    posts, total = await service.list_posts(skip=0, limit=2)

    assert len(posts) == 2
    assert total == 3
    assert posts[0].created_at > posts[1].created_at
