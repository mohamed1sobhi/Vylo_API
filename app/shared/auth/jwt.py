from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Sequence
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from jose import JWTError, jwt

from app.shared.config.settings import settings
from app.shared.exceptions.handlers import UnauthorizedError


password_hasher = PasswordHasher()


def _encode_token(
    user_id: UUID | str,
    token_type: str,
    expires_delta: timedelta,
    system_permissions: Sequence[str] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    issued_at = int(now.timestamp())
    expires_at = int((now + expires_delta).timestamp())
    payload = {
        "user_id": str(user_id),
        "system_permissions": list(system_permissions or []),
        "token_type": token_type,
        "iat": issued_at,
        "nbf": issued_at,
        "exp": expires_at,
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: UUID | str, system_permissions: Sequence[str]) -> str:
    return _encode_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        system_permissions=system_permissions,
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


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_password",
    "verify_password",
]