from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database.session import Base


def _utcnow() -> datetime:
	return datetime.now(timezone.utc)


class AdminUser(Base):
	__tablename__ = "users"
	__table_args__ = {"schema": "admins"}

	id: Mapped[UUID] = mapped_column(primary_key=True)
	username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
	hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

	user_roles: Mapped[list[UserRole]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Role(Base):
	__tablename__ = "roles"
	__table_args__ = {"schema": "admins"}

	id: Mapped[UUID] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)

	role_permissions: Mapped[list[RolePermission]] = relationship(
		back_populates="role",
		cascade="all, delete-orphan",
	)
	user_roles: Mapped[list[UserRole]] = relationship(back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
	__tablename__ = "permissions"
	__table_args__ = {"schema": "admins"}

	id: Mapped[UUID] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)

	role_permissions: Mapped[list[RolePermission]] = relationship(
		back_populates="permission",
		cascade="all, delete-orphan",
	)


class RolePermission(Base):
	__tablename__ = "role_permissions"
	__table_args__ = {"schema": "admins"}

	role_id: Mapped[UUID] = mapped_column(ForeignKey("admins.roles.id", ondelete="CASCADE"), primary_key=True)
	permission_id: Mapped[UUID] = mapped_column(
		ForeignKey("admins.permissions.id", ondelete="CASCADE"),
		primary_key=True,
	)

	role: Mapped[Role] = relationship(back_populates="role_permissions")
	permission: Mapped[Permission] = relationship(back_populates="role_permissions")


class UserRole(Base):
	__tablename__ = "user_roles"
	__table_args__ = {"schema": "admins"}

	user_id: Mapped[UUID] = mapped_column(ForeignKey("admins.users.id", ondelete="CASCADE"), primary_key=True)
	role_id: Mapped[UUID] = mapped_column(ForeignKey("admins.roles.id", ondelete="CASCADE"), primary_key=True)
	assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

	user: Mapped[AdminUser] = relationship(back_populates="user_roles")
	role: Mapped[Role] = relationship(back_populates="user_roles")


__all__ = ["AdminUser", "Permission", "Role", "RolePermission", "UserRole"]
