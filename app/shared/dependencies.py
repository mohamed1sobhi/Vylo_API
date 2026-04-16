from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Sequence
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from app.config import settings
from app.shared.exceptions import ForbiddenError, UnauthorizedError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
password_hasher = PasswordHasher()


class TokenPayload(BaseModel):
    user_id: UUID
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    token_type: Literal["access", "refresh"] = "access"
    iat: int
    nbf: int
    exp: int
    jti: UUID


def _encode_token(
    user_id: UUID | str,
    token_type: Literal["access", "refresh"],
    expires_delta: timedelta,
    roles: Sequence[str] | None = None,
    permissions: Sequence[str] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    issued_at = int(now.timestamp())
    expires_at = int((now + expires_delta).timestamp())
    payload = {
        "user_id": str(user_id),
        "roles": list(roles or []),
        "permissions": list(permissions or []),
        "token_type": token_type,
        "iat": issued_at,
        "nbf": issued_at,
        "exp": expires_at,
        "jti": str(uuid4()),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    user_id: UUID | str,
    roles: Sequence[str],
    permissions: Sequence[str] | None = None,
) -> str:
    return _encode_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        roles=roles,
        permissions=permissions,
    )


def create_refresh_token(user_id: UUID | str) -> str:
    return _encode_token(
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    if not isinstance(payload, dict):
        raise UnauthorizedError("Invalid token payload")

    return payload


def hash_password(plain: str) -> str:
    return password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return password_hasher.verify(hashed, plain)
    except (InvalidHashError, VerificationError, VerifyMismatchError, TypeError, ValueError):
        return False


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> TokenPayload:
    if not token:
        raise UnauthorizedError("Not authenticated")

    payload = decode_token(token)

    try:
        current_user = TokenPayload.model_validate(payload)
    except PydanticValidationError as exc:
        raise UnauthorizedError("Invalid token payload") from exc

    if current_user.token_type != "access":
        raise UnauthorizedError("Access token required")

    return current_user


def require_permission(permission_name: str):
    async def dependency(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if permission_name not in current_user.permissions:
            raise ForbiddenError(f"Missing required permission: {permission_name}")

        return current_user

    return dependency


__all__ = [
    "TokenPayload",
    "oauth2_scheme",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_password",
    "verify_password",
    "get_current_user",
    "require_permission",
]
