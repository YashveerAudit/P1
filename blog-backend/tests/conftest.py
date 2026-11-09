import os

# Settings require these; tests never connect to a real database.
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("JWT_SECRET", "test-secret-that-is-at-least-32-characters-long")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.dependencies import get_post_repository, get_user_repository  # noqa: E402
from app.main import app  # noqa: E402
from tests.fakes import InMemoryPostRepository, InMemoryUserRepository  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def repository():
    return InMemoryPostRepository()


@pytest.fixture
def user_repository():
    return InMemoryUserRepository()


@pytest.fixture
def client(repository, user_repository):
    # TestClient is not used as a context manager, so the startup hook that
    # connects to MongoDB never runs; the in-memory repositories are used instead.
    app.dependency_overrides[get_post_repository] = lambda: repository
    app.dependency_overrides[get_user_repository] = lambda: user_repository
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def valid_post():
    return {
        "title": "My first post",
        "content": "This is the body of my first blog post.",
    }


@pytest.fixture
def valid_user():
    return {"email": "yash@example.com", "name": "Yashveer", "password": "correct-horse-battery"}


def register(client, user):
    """Register a user and return (auth headers, user json)."""
    response = client.post("/api/auth/register", json=user)
    assert response.status_code == 201, response.text
    body = response.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]


@pytest.fixture
def auth(client, valid_user):
    """Headers for a signed-in user, plus that user's public details."""
    headers, user = register(client, valid_user)
    return {"headers": headers, "user": user}


@pytest.fixture
def other_auth(client):
    """A second, different signed-in user."""
    headers, user = register(
        client, {"email": "someone.else@example.com", "name": "Someone Else", "password": "another-long-password"}
    )
    return {"headers": headers, "user": user}
