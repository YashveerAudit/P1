"""Wires repositories and services into routes via FastAPI's Depends().

Tests replace `get_post_repository` with an in-memory implementation.
"""
from fastapi import Depends, Request
from typing_extensions import Annotated

from app.repositories.post_repository import MongoPostRepository, PostRepository
from app.services.post_service import PostService

POSTS_COLLECTION = "posts"


def get_post_repository(request: Request) -> PostRepository:
    return MongoPostRepository(request.app.state.db[POSTS_COLLECTION])


def get_post_service(
    repository: Annotated[PostRepository, Depends(get_post_repository)],
) -> PostService:
    return PostService(repository)


PostServiceDep = Annotated[PostService, Depends(get_post_service)]
