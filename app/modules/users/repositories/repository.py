from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models.models import User, UserProfile


class UserRepository:
	def __init__(self, session: AsyncSession) -> None:
		self._session = session

	async def get_by_id(self, user_id: UUID) -> User | None:
		statement = select(User).where(User.id == user_id)
		return await self._session.scalar(statement)

	async def get_by_email(self, email: str) -> User | None:
		statement = select(User).where(User.email == email)
		return await self._session.scalar(statement)

	async def get_by_username(self, username: str) -> User | None:
		statement = select(User).where(User.username == username)
		return await self._session.scalar(statement)

	async def create(self, data: dict[str, Any]) -> User:
		user = User(**data)
		self._session.add(user)
		await self._session.flush()
		return user

	async def update_user(self, user_id: UUID, data: dict[str, Any]) -> User | None:
		user = await self.get_by_id(user_id)
		if user is None:
			return None

		for field_name, value in data.items():
			setattr(user, field_name, value)

		await self._session.flush()
		return user

	async def deactivate_user(self, user_id: UUID) -> User | None:
		user = await self.get_by_id(user_id)
		if user is None:
			return None

		user.is_active = False
		await self._session.flush()
		return user

	async def get_profile(self, user_id: UUID) -> UserProfile | None:
		statement = select(UserProfile).where(UserProfile.user_id == user_id)
		return await self._session.scalar(statement)

	async def upsert_profile(self, user_id: UUID, data: dict[str, Any]) -> UserProfile:
		profile = await self.get_profile(user_id)

		if profile is None:
			profile = UserProfile(user_id=user_id, **data)
			self._session.add(profile)
		else:
			for field_name, value in data.items():
				setattr(profile, field_name, value)
			profile.updated_at = datetime.now(timezone.utc)

		await self._session.flush()
		return profile


__all__ = ["UserRepository"]
