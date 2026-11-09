"""The User domain model. The password hash never leaves the backend."""
from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    name: str
    password_hash: str
    created_at: datetime
