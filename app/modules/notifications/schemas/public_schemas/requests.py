from __future__ import annotations

from typing import Any, Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateNotificationRequest(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True)

	recipient_id: UUID
	type: Annotated[str, Field(min_length=1, max_length=100)]
	payload: dict[str, Any]


class NotificationLookupRequest(BaseModel):
	notification_id: UUID
	user_id: UUID


class NotificationListRequest(BaseModel):
	user_id: UUID
	limit: Annotated[int, Field(ge=1, le=100)] = 50
	offset: Annotated[int, Field(ge=0)] = 0


class MarkAllNotificationsReadRequest(BaseModel):
	user_id: UUID


__all__ = [
	"CreateNotificationRequest",
	"MarkAllNotificationsReadRequest",
	"NotificationListRequest",
	"NotificationLookupRequest",
]
