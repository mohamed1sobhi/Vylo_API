from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from app.modules.users.schemas.public_schemas.requests import UserLookupRequest


class UserServiceProtocol(Protocol):
	async def get_user(self, user_id: UUID | str) -> dict[str, Any]: ...
	async def get_profile(self, user_id: UUID | str) -> dict[str, Any]: ...


class UserFacade:
	def __init__(self, service: UserServiceProtocol) -> None:
		self._service = service

	async def get_user_by_id(self, user_id: UUID | str) -> dict[str, Any]:
		request = UserLookupRequest(user_id=user_id)
		return await self._service.get_user(request.user_id)

	async def get_profile(self, user_id: UUID | str) -> dict[str, Any]:
		request = UserLookupRequest(user_id=user_id)
		return await self._service.get_profile(request.user_id)


__all__ = ["UserFacade"]