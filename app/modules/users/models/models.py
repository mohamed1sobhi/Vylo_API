from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database.session import Base


def _utcnow() -> datetime:
	return datetime.now(timezone.utc)


class User(Base):
	__tablename__ = "users"
	__table_args__ = {"schema": "users"}

	id: Mapped[UUID] = mapped_column(primary_key=True)
	username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
	hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

	profile: Mapped[UserProfile | None] = relationship(back_populates="user", uselist=False)


class UserProfile(Base):
	__tablename__ = "user_profiles"
	__table_args__ = {"schema": "users"}

	id: Mapped[UUID] = mapped_column(primary_key=True)
	user_id: Mapped[UUID] = mapped_column(
		ForeignKey("users.users.id", ondelete="CASCADE"),
		unique=True,
		index=True,
		nullable=False,
	)
	display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
	bio: Mapped[str | None] = mapped_column(Text, nullable=True)
	avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		nullable=False,
		default=_utcnow,
		onupdate=_utcnow,
	)

	user: Mapped[User] = relationship(back_populates="profile")


__all__ = ["User", "UserProfile"]
