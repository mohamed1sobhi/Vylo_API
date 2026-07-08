from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	recipient_id: UUID
	type: str
	payload: dict[str, Any]
	is_read: bool
	created_at: datetime


class NotificationListResponse(BaseModel):
	notifications: list[NotificationResponse]


class NotificationReadAllResponse(BaseModel):
	detail: str


class NotificationWebSocketAuthPayload(BaseModel):
	token: str


__all__ = [
	"NotificationListResponse",
	"NotificationReadAllResponse",
	"NotificationResponse",
	"NotificationWebSocketAuthPayload",
]
