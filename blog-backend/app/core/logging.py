"""Logging setup and a middleware that logs every request."""
import logging
import time
import uuid

from fastapi import FastAPI, Request

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s - %(message)s"

logger = logging.getLogger("app.requests")


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level.upper(), format=LOG_FORMAT)


def add_request_logging(app: FastAPI) -> None:
    """Log method, path, status and duration for each request.

    Each request gets an ID (returned in the X-Request-ID header) so a log line
    can be matched to the response a user saw.
    """

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.1f ms) [request_id=%s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )
        response.headers["X-Request-ID"] = request_id
        return response
