"""Unit tests for PostService business rules, independent of HTTP."""
from datetime import datetime, timedelta, timezone

import pytest

from app.core.exceptions import PermissionDeniedError, PostNotFoundError
from app.models.user import User
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


def make_user(user_id: str, name: str) -> User:
    return User(
        id=user_id,
        email=f"{user_id}@example.com",
        name=name,
        password_hash="not-used-here",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def service(clock):
    return PostService(InMemoryPostRepository(), clock=clock)


@pytest.fixture
def ana():
    return make_user("user-ana", "Ana")


@pytest.fixture
def ben():
    return make_user("user-ben", "Ben")


@pytest.fixture
def payload():
    return PostCreate(title="Hello world", content="Some content here.")


async def test_create_sets_author_owner_and_timestamps(service, clock, payload, ana):
    post = await service.create_post(payload, ana)

    assert post.author == "Ana"
    assert post.owner_id == ana.id
    assert post.created_at == clock.now
    assert post.updated_at == clock.now


async def test_update_changes_updated_at_but_not_created_at(service, clock, payload, ana):
    post = await service.create_post(payload, ana)
    clock.advance(minutes=5)

    updated = await service.update_post(post.id, PostUpdate(title="New title", content=payload.content), ana)

    assert updated.title == "New title"
    assert updated.created_at == post.created_at
    assert updated.updated_at == post.created_at + timedelta(minutes=5)


async def test_only_owner_can_update(service, payload, ana, ben):
    post = await service.create_post(payload, ana)

    with pytest.raises(PermissionDeniedError):
        await service.update_post(post.id, PostUpdate(title="Hijacked", content=payload.content), ben)

    assert (await service.get_post(post.id)).title == "Hello world"


async def test_only_owner_can_delete(service, payload, ana, ben):
    post = await service.create_post(payload, ana)

    with pytest.raises(PermissionDeniedError):
        await service.delete_post(post.id, ben)

    await service.delete_post(post.id, ana)
    with pytest.raises(PostNotFoundError):
        await service.get_post(post.id)


async def test_get_missing_post_raises_not_found(service):
    with pytest.raises(PostNotFoundError):
        await service.get_post("missing")


async def test_update_missing_post_raises_not_found(service, payload, ana):
    with pytest.raises(PostNotFoundError):
        await service.update_post("missing", PostUpdate(**payload.model_dump()), ana)


async def test_delete_missing_post_raises_not_found(service, ana):
    with pytest.raises(PostNotFoundError):
        await service.delete_post("missing", ana)


async def test_list_returns_total_count_independent_of_page_size(service, clock, payload, ana):
    for _ in range(3):
        await service.create_post(payload, ana)
        clock.advance(minutes=1)

    posts, total = await service.list_posts(skip=0, limit=2)

    assert len(posts) == 2
    assert total == 3
    assert posts[0].created_at > posts[1].created_at
