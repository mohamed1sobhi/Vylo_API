from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class CommunityLookupRequest(BaseModel):
	community_id: UUID


class CommunityMembershipLookupRequest(BaseModel):
	community_id: UUID
	user_id: UUID


__all__ = ["CommunityLookupRequest", "CommunityMembershipLookupRequest"]