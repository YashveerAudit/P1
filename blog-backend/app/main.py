"""Application entry point: builds the FastAPI app.

Run locally (from the blog-backend folder):
    uvicorn app.main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import AsyncMongoClient

from app.api.routes import posts
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import add_request_logging, configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open the MongoDB connection on startup and close it on shutdown."""
    settings = get_settings()
    client = AsyncMongoClient(settings.mongo_uri, tz_aware=True)
    app.state.db = client[settings.mongo_db_name]
    logger.info("Connected to MongoDB database '%s'", settings.mongo_db_name)
    try:
        yield
    finally:
        await client.close()
        logger.info("MongoDB connection closed")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        description="RESTful API for managing blog posts.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Only the configured frontend origins may call the API from a browser.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
    add_request_logging(app)
    register_exception_handlers(app)

    app.include_router(posts.router)

    @app.get("/api/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
