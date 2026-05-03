from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class AdminUserLookupRequest(BaseModel):
	user_id: UUID


__all__ = ["AdminUserLookupRequest"]