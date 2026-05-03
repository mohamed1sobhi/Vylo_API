from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from app.modules.admins.schemas.public_schemas.requests import AdminUserLookupRequest


class AdminServiceProtocol(Protocol):
	async def get_system_user(self, user_id: UUID | str) -> dict[str, Any]: ...
	async def get_permissions_for_user(self, user_id: UUID | str) -> dict[str, Any]: ...


class AdminFacade:
	def __init__(self, service: AdminServiceProtocol) -> None:
		self._service = service

	async def get_system_user(self, user_id: UUID | str) -> dict[str, Any]:
		request = AdminUserLookupRequest(user_id=user_id)
		return await self._service.get_system_user(request.user_id)

	async def get_permissions_for_user(self, user_id: UUID | str) -> dict[str, Any]:
		request = AdminUserLookupRequest(user_id=user_id)
		return await self._service.get_permissions_for_user(request.user_id)


__all__ = ["AdminFacade"]