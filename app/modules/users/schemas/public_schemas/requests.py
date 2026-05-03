from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class UserLookupRequest(BaseModel):
	user_id: UUID


__all__ = ["UserLookupRequest"]