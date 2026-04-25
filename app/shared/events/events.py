from __future__ import annotations

from dataclasses import dataclass

from app.shared.events.base import DomainEvent


@dataclass(kw_only=True, slots=True)
class UserRegisteredEvent(DomainEvent):
    user_id: str
    username: str


@dataclass(kw_only=True, slots=True)
class FriendRequestSentEvent(DomainEvent):
    requester_id: str
    target_id: str


@dataclass(kw_only=True, slots=True)
class FriendshipFormedEvent(DomainEvent):
    user_id_a: str
    user_id_b: str


@dataclass(kw_only=True, slots=True)
class MemberJoinedEvent(DomainEvent):
    user_id: str
    community_id: str


@dataclass(kw_only=True, slots=True)
class MemberLeftEvent(DomainEvent):
    user_id: str
    community_id: str


@dataclass(kw_only=True, slots=True)
class PostCreatedEvent(DomainEvent):
    post_id: str
    author_id: str
    community_id: str | None
    visibility: str


__all__ = [
    "FriendRequestSentEvent",
    "FriendshipFormedEvent",
    "MemberJoinedEvent",
    "MemberLeftEvent",
    "PostCreatedEvent",
    "UserRegisteredEvent",
]