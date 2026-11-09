"""Request/response schemas for registration, login and the current user."""
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints
from typing_extensions import Annotated

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=80)]
# No max length other than a sanity cap: long passphrases are good passwords.
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UserRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    name: Name
    password: Password


class UserLogin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: Password


class UserResponse(BaseModel):
    """Public view of a user: never includes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
