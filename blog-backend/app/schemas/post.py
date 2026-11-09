"""Request and response schemas: what the API accepts and what it returns.

Input and output are deliberately separate models, so clients cannot set
server-controlled fields such as id, author, owner or timestamps.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated

# Leading/trailing whitespace is stripped before length checks,
# so "   " is rejected rather than accepted as a title.
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=150)]
Content = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20_000)]


class PostCreate(BaseModel):
    """Body for creating a post. The author is the signed-in user.

    Unknown fields (e.g. "_id", "author", "owner_id") are rejected.
    """

    model_config = ConfigDict(extra="forbid")

    title: Title
    content: Content


class PostUpdate(PostCreate):
    """Body for replacing a post (PUT): all fields are required."""


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    content: str
    author: str
    owner_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    items: List[PostResponse]
    total: int
    skip: int
    limit: int
