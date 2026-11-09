"""HTTP endpoints for blog posts. Kept thin: validate input, call the service."""
from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import PostServiceDep
from app.schemas.post import PostCreate, PostListResponse, PostResponse, PostUpdate

router = APIRouter(prefix="/api/posts", tags=["posts"])

NOT_FOUND = {404: {"description": "Post not found"}}


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostCreate, service: PostServiceDep):
    return await service.create_post(payload)


@router.get("", response_model=PostListResponse)
async def list_posts(
    service: PostServiceDep,
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum posts to return"),
):
    posts, total = await service.list_posts(skip=skip, limit=limit)
    return PostListResponse(
        items=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{post_id}", response_model=PostResponse, responses=NOT_FOUND)
async def get_post(post_id: str, service: PostServiceDep):
    return await service.get_post(post_id)


@router.put("/{post_id}", response_model=PostResponse, responses=NOT_FOUND)
async def update_post(post_id: str, payload: PostUpdate, service: PostServiceDep):
    return await service.update_post(post_id, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
async def delete_post(post_id: str, service: PostServiceDep):
    await service.delete_post(post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
