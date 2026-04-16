from fastapi import HTTPException


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


__all__ = [
    "AppHTTPException",
    "NotFoundError",
    "ConflictError",
    "ForbiddenError",
    "UnauthorizedError",
    "ValidationError",
]
