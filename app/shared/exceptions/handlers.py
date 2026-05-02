from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppHTTPException(HTTPException):
    status_code = 500
    default_detail = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(status_code=self.status_code, detail=detail or self.default_detail)


class NotFoundError(AppHTTPException):
    status_code = 404
    default_detail = "Resource not found"


class ConflictError(AppHTTPException):
    status_code = 409
    default_detail = "Duplicate resource"


class ForbiddenError(AppHTTPException):
    status_code = 403
    default_detail = "Permission denied"


class UnauthorizedError(AppHTTPException):
    status_code = 401
    default_detail = "Authentication failed"


class ValidationError(AppHTTPException):
    status_code = 422
    default_detail = "Business rule violation"


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


__all__ = [
    "AppHTTPException",
    "ConflictError",
    "ForbiddenError",
    "NotFoundError",
    "UnauthorizedError",
    "ValidationError",
    "register_exception_handlers",
]