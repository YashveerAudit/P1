"""Domain errors and the handlers that turn every error into one JSON shape.

Every error response looks like:
    {"error": {"code": "...", "message": "...", "details": [...]}}
so the frontend only has to handle a single format.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for errors the API reports deliberately."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "internal_error"
    headers: Dict[str, str] = {}

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class PostNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "post_not_found"

    def __init__(self, post_id: str):
        super().__init__(f"Post with id '{post_id}' was not found.")


class AuthenticationError(AppError):
    """No token, or an invalid/expired one."""

    status_code = status.HTTP_401_UNAUTHORIZED
    code = "not_authenticated"
    headers = {"WWW-Authenticate": "Bearer"}

    def __init__(self, message: str = "You need to be signed in to do this."):
        super().__init__(message)


class InvalidCredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "invalid_credentials"

    def __init__(self):
        super().__init__("Incorrect email or password.")


class PermissionDeniedError(AppError):
    """Signed in, but not allowed to touch this resource."""

    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"

    def __init__(self, message: str = "You can only edit or delete your own posts."):
        super().__init__(message)


class EmailAlreadyRegisteredError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "email_already_registered"

    def __init__(self):
        super().__init__("An account with this email already exists.")


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[List[Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        logger.info("%s: %s", exc.code, exc.message)
        return error_response(exc.status_code, exc.code, exc.message, headers=exc.headers or None)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        details = [
            {
                # loc looks like ("body", "title"); drop the "body"/"query" prefix
                "field": ".".join(str(part) for part in err["loc"][1:]) or str(err["loc"][0]),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return error_response(
            422,
            "validation_error",
            "The request data is invalid.",
            details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException):
        return error_response(exc.status_code, "http_error", str(exc.detail))

    @app.exception_handler(PyMongoError)
    async def handle_database_error(request: Request, exc: PyMongoError):
        logger.exception("Database error while handling %s %s", request.method, request.url.path)
        return error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "database_unavailable",
            "The database is currently unavailable. Please try again later.",
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        # Log the full traceback, but never leak internals to the client.
        logger.exception("Unhandled error while handling %s %s", request.method, request.url.path)
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            "An unexpected error occurred.",
        )
