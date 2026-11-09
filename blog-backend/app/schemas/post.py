"""Request and response schemas: what the API accepts and what it returns.

Input and output are deliberately separate models, so clients cannot set
server-controlled fields such as id or timestamps.
"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated

# Leading/trailing whitespace is stripped before length checks,
# so "   " is rejected rather than accepted as a title.
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=150)]
Content = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20_000)]
Author = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=80)]


class PostCreate(BaseModel):
    """Body for creating a post. Unknown fields (e.g. "_id") are rejected."""

    model_config = ConfigDict(extra="forbid")

    title: Title
    content: Content
    author: Author


class PostUpdate(PostCreate):
    """Body for replacing a post (PUT): all fields are required."""


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    content: str
    author: str
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    items: List[PostResponse]
    total: int
    skip: int
    limit: int
