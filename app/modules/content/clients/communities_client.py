from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from app.modules.content.schemas.public_schemas.responses import ContentCommunityMembershipResponse


class CommunityFacadeProtocol(Protocol):
	async def is_member(self, user_id: UUID | str, community_id: UUID | str) -> dict[str, Any]: ...


class CommunitiesClient:
	def __init__(self, communities_facade: CommunityFacadeProtocol) -> None:
		self._communities_facade = communities_facade

	async def is_member(self, user_id: UUID | str, community_id: UUID | str) -> dict[str, Any]:
		payload = await self._communities_facade.is_member(user_id, community_id)
		response = ContentCommunityMembershipResponse.model_validate(payload)
		return response.model_dump()


__all__ = ["CommunitiesClient"]
