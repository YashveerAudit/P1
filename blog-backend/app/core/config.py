"""Application settings, loaded from environment variables or a local .env file.

Secrets such as the MongoDB connection string are never hard-coded in source.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Blog Post Manager API"
    mongo_uri: str
    mongo_db_name: str = "blog_database"
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read once per process)."""
    return Settings()
