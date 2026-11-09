"""Wires repositories and services into routes via FastAPI's Depends().

Tests replace `get_post_repository` / `get_user_repository` with in-memory
implementations.
"""
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing_extensions import Annotated

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.post_repository import MongoPostRepository, PostRepository
from app.repositories.user_repository import MongoUserRepository, UserRepository
from app.services.auth_service import AuthService
from app.services.post_service import PostService

POSTS_COLLECTION = "posts"
USERS_COLLECTION = "users"

# auto_error=False lets us return our standard error format instead of FastAPI's.
bearer_scheme = HTTPBearer(auto_error=False)


# --- Repositories & services --------------------------------------------------


def get_post_repository(request: Request) -> PostRepository:
    return MongoPostRepository(request.app.state.db[POSTS_COLLECTION])


def get_user_repository(request: Request) -> UserRepository:
    return MongoUserRepository(request.app.state.db[USERS_COLLECTION])


def get_post_service(
    repository: Annotated[PostRepository, Depends(get_post_repository)],
) -> PostService:
    return PostService(repository)


def get_auth_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(repository)


PostServiceDep = Annotated[PostService, Depends(get_post_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


# --- Current user -------------------------------------------------------------


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Resolve the `Authorization: Bearer <token>` header to a User, or raise 401."""
    if credentials is None:
        raise AuthenticationError()

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise AuthenticationError("Your session is invalid or has expired. Please sign in again.")

    user = await users.get_by_id(user_id)
    if user is None:
        raise AuthenticationError("This account no longer exists.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
