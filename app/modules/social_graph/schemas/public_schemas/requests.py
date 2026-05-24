from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class SocialGraphUserLookupRequest(BaseModel):
	user_id: UUID


__all__ = ["SocialGraphUserLookupRequest"]