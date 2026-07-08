from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from app.modules.notifications.schemas.public_schemas.responses import NotificationUserContactResponse


class UserFacadeProtocol(Protocol):
	async def get_user_by_id(self, user_id: UUID | str) -> dict[str, Any]: ...


class UsersClient:
	def __init__(self, users_facade: UserFacadeProtocol) -> None:
		self._users_facade = users_facade

	async def get_contact(self, user_id: UUID | str) -> dict[str, Any]:
		payload = await self._users_facade.get_user_by_id(user_id)
		response = NotificationUserContactResponse.model_validate(payload)
		return response.model_dump()


__all__ = ["UsersClient"]
