from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SendFriendRequestRequest(BaseModel):
	receiver_id: UUID


class FriendRequestResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	requester_id: UUID
	receiver_id: UUID
	status: Literal["pending", "rejected"]
	created_at: datetime
	updated_at: datetime


class FriendshipResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	user_low: UUID
	user_high: UUID
	created_at: datetime


class FriendListResponse(BaseModel):
	user_id: UUID
	friend_ids: list[UUID]


class PendingFriendRequestsResponse(BaseModel):
	user_id: UUID
	requests: list[FriendRequestResponse]


__all__ = [
	"FriendListResponse",
	"FriendRequestResponse",
	"FriendshipResponse",
	"PendingFriendRequestsResponse",
	"SendFriendRequestRequest",
]