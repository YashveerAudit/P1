import os

# Settings require a connection string; tests never connect to it.
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.dependencies import get_post_repository  # noqa: E402
from app.main import app  # noqa: E402
from tests.fakes import InMemoryPostRepository  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def repository():
    return InMemoryPostRepository()


@pytest.fixture
def client(repository):
    # TestClient is not used as a context manager, so the startup hook that
    # connects to MongoDB never runs; the in-memory repository is used instead.
    app.dependency_overrides[get_post_repository] = lambda: repository
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def valid_post():
    return {
        "title": "My first post",
        "content": "This is the body of my first blog post.",
        "author": "Yashveer",
    }
