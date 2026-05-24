from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from app.modules.social_graph.schemas.public_schemas.requests import SocialGraphUserLookupRequest


class SocialGraphServiceProtocol(Protocol):
	async def get_friends(self, user_id: UUID | str) -> dict[str, Any]: ...
	async def get_pending_requests(self, user_id: UUID | str) -> dict[str, Any]: ...


class SocialGraphFacade:
	def __init__(self, service: SocialGraphServiceProtocol) -> None:
		self._service = service

	async def get_friends(self, user_id: UUID | str) -> dict[str, Any]:
		request = SocialGraphUserLookupRequest(user_id=user_id)
		return await self._service.get_friends(request.user_id)

	async def get_pending_requests(self, user_id: UUID | str) -> dict[str, Any]:
		request = SocialGraphUserLookupRequest(user_id=user_id)
		return await self._service.get_pending_requests(request.user_id)


__all__ = ["SocialGraphFacade"]