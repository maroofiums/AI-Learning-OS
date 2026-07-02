"""
Domain exception hierarchy and FastAPI exception handlers.

Rule: service-layer code raises these exceptions, never `HTTPException`
directly. This keeps the service layer framework-agnostic (per
ARCHITECTURE.md: "business logic should never depend directly on the web
framework") — routers stay thin, and services stay unit-testable without
spinning up FastAPI at all.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base class for all application-raised exceptions."""

    status_code: int = 500
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundException(AppException):
    status_code = 404
    default_message = "Resource not found."


class UnauthorizedException(AppException):
    status_code = 401
    default_message = "Authentication required or credentials invalid."


class ForbiddenException(AppException):
    status_code = 403
    default_message = "You do not have permission to perform this action."


class ConflictException(AppException):
    status_code = 409
    default_message = "Resource already exists or state conflict."


class ValidationException(AppException):
    status_code = 422
    default_message = "Invalid input."


def register_exception_handlers(app: FastAPI) -> None:
    """Wire every AppException subclass to a consistent JSON error response."""

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("AppException on %s %s: %s", request.method, request.url.path, exc.message)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        # Never leak internal error details to the client — log the real
        # exception server-side, return a generic message to the caller.
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})