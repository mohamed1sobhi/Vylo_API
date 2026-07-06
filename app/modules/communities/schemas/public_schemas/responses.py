from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class CommunityUserResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	username: str
	email: EmailStr
	is_active: bool
	created_at: datetime


__all__ = ["CommunityUserResponse"]