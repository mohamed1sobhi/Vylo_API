from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class NotificationUserContactResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	username: str
	email: EmailStr
	is_active: bool
	created_at: datetime
	phone_number: str | None = None


class NotificationCommunityOwnerResponse(BaseModel):
	community_id: UUID
	owner_id: UUID


class NotificationCommunityMembersResponse(BaseModel):
	community_id: UUID
	member_ids: list[UUID]


class NotificationResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	recipient_id: UUID
	type: str
	payload: dict[str, Any]
	is_read: bool
	created_at: datetime


__all__ = [
	"NotificationCommunityMembersResponse",
	"NotificationCommunityOwnerResponse",
	"NotificationResponse",
	"NotificationUserContactResponse",
]
