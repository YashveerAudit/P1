"""The Post domain model, independent of the database and the HTTP layer."""
from datetime import datetime

from pydantic import BaseModel


class Post(BaseModel):
    id: str
    title: str
    content: str
    author: str
    created_at: datetime
    updated_at: datetime
