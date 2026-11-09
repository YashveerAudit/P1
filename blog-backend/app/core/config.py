"""Application settings, loaded from environment variables or a local .env file.

Secrets such as the MongoDB connection string and the JWT signing key are
never hard-coded in source.
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Blog Post Manager API"
    mongo_uri: str
    mongo_db_name: str = "blog_database"
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    log_level: str = "INFO"

    # Authentication
    jwt_secret: str = Field(min_length=32, description="Random secret used to sign tokens")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read once per process)."""
    return Settings()
