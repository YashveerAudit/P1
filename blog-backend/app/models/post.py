"""The Post domain model, independent of the database and the HTTP layer."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Post(BaseModel):
    id: str
    title: str
    content: str
    author: str
    # Id of the user who created the post. Only they may edit or delete it.
    # Optional so posts created before authentication existed still load.
    owner_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
