from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID, uuid4

from app.shared.events.bus import bus
from app.shared.events.events import PostCreatedEvent
from app.shared.exceptions.handlers import ForbiddenError, NotFoundError, ValidationError


CONTENT_POSTS_DELETE_PERMISSION = "content.posts.delete"


class ContentRepositoryProtocol(Protocol):
	async def create(self, data: dict[str, Any]) -> Any: ...
	async def get_by_id(self, post_id: UUID) -> Any | None: ...
	async def get_public_feed(self, limit: int, offset: int) -> list[Any]: ...
	async def get_user_posts(self, author_id: UUID, viewer_id: UUID | None) -> list[Any]: ...
	async def get_community_posts(self, community_id: UUID, limit: int, offset: int) -> list[Any]: ...
	async def soft_delete(self, post_id: UUID) -> bool: ...


class CommunitiesClientProtocol(Protocol):
	async def is_member(self, user_id: UUID | str, community_id: UUID | str) -> dict[str, Any]: ...


class ContentService:
	def __init__(self, repo: ContentRepositoryProtocol, communities_client: CommunitiesClientProtocol) -> None:
		self._repo = repo
		self._communities_client = communities_client

	async def create_post(self, author_id: UUID | str, data: dict[str, Any]) -> dict[str, Any]:
		normalized_author_id = self._parse_uuid(author_id, label="author id")
		visibility = self._normalize_visibility(data.get("visibility", "public"))
		community_id = self._normalize_optional_uuid(data.get("community_id"), label="community id")

		if visibility == "community":
			if community_id is None:
				raise ValidationError("Community posts require a community id")
			await self._require_community_member(normalized_author_id, community_id)
		elif community_id is not None:
			raise ValidationError("Only community-visible posts may include a community id")

		post = await self._repo.create(
			{
				"id": uuid4(),
				"author_id": normalized_author_id,
				"community_id": community_id,
				"visibility": visibility,
				"title": self._normalize_optional_text(data.get("title"), label="title", max_length=200),
				"body": self._normalize_required_text(data.get("body"), label="body"),
			}
		)

		await bus.publish(
			PostCreatedEvent(
				post_id=str(post.id),
				author_id=str(post.author_id),
				community_id=str(post.community_id) if post.community_id is not None else None,
				visibility=self._coerce_visibility(post.visibility),
			)
		)
		return self._post_to_payload(post)

	async def get_post(self, post_id: UUID | str, viewer_id: UUID | str | None) -> dict[str, Any]:
		normalized_post_id = self._parse_uuid(post_id, label="post id")
		normalized_viewer_id = self._parse_optional_uuid(viewer_id, label="viewer id")

		post = await self._require_existing_post(normalized_post_id)
		await self._enforce_post_visibility(post, normalized_viewer_id)
		return self._post_to_payload(post)

	async def list_public_feed(self, *, limit: int, offset: int) -> dict[str, Any]:
		normalized_limit = self._normalize_limit(limit)
		normalized_offset = self._normalize_offset(offset)
		posts = await self._repo.get_public_feed(normalized_limit, normalized_offset)
		return {"posts": [self._post_to_payload(post) for post in posts]}

	async def list_user_posts(
		self,
		author_id: UUID | str,
		viewer_id: UUID | str | None,
	) -> dict[str, Any]:
		normalized_author_id = self._parse_uuid(author_id, label="author id")
		normalized_viewer_id = self._parse_optional_uuid(viewer_id, label="viewer id")

		posts = await self._repo.get_user_posts(normalized_author_id, normalized_viewer_id)
		visible_posts: list[Any] = []
		for post in posts:
			if await self._can_view_post(post, normalized_viewer_id):
				visible_posts.append(post)
		return {
			"author_id": normalized_author_id,
			"posts": [self._post_to_payload(post) for post in visible_posts],
		}

	async def list_community_posts(
		self,
		community_id: UUID | str,
		viewer_id: UUID | str,
		*,
		limit: int,
		offset: int,
	) -> dict[str, Any]:
		normalized_community_id = self._parse_uuid(community_id, label="community id")
		normalized_viewer_id = self._parse_uuid(viewer_id, label="viewer id")
		normalized_limit = self._normalize_limit(limit)
		normalized_offset = self._normalize_offset(offset)

		await self._require_community_member(normalized_viewer_id, normalized_community_id)
		posts = await self._repo.get_community_posts(normalized_community_id, normalized_limit, normalized_offset)
		return {
			"community_id": normalized_community_id,
			"posts": [self._post_to_payload(post) for post in posts],
		}

	async def delete_post(
		self,
		post_id: UUID | str,
		requester_id: UUID | str,
		*,
		can_delete_any: bool = False,
	) -> None:
		normalized_post_id = self._parse_uuid(post_id, label="post id")
		normalized_requester_id = self._parse_uuid(requester_id, label="requester id")

		post = await self._require_existing_post(normalized_post_id)
		if post.author_id != normalized_requester_id and not can_delete_any:
			raise ForbiddenError("Only the author can delete this post")

		deleted = await self._repo.soft_delete(normalized_post_id)
		if not deleted:
			raise NotFoundError("Post not found")

	async def _require_existing_post(self, post_id: UUID) -> Any:
		post = await self._repo.get_by_id(post_id)
		if post is None:
			raise NotFoundError("Post not found")
		return post

	async def _enforce_post_visibility(self, post: Any, viewer_id: UUID | None) -> None:
		if await self._can_view_post(post, viewer_id):
			return
		raise ForbiddenError("You cannot view this post")

	async def _can_view_post(self, post: Any, viewer_id: UUID | None) -> bool:
		visibility = self._coerce_visibility(post.visibility)
		if visibility == "public":
			return True
		if viewer_id is None:
			return False
		if visibility == "private" and post.author_id == viewer_id:
			return True
		if visibility == "community" and post.community_id is not None:
			membership = await self._communities_client.is_member(viewer_id, post.community_id)
			return bool(membership.get("is_member", False))
		return False

	async def _require_community_member(self, user_id: UUID, community_id: UUID) -> None:
		membership = await self._communities_client.is_member(user_id, community_id)
		if not membership.get("is_member", False):
			raise ForbiddenError("Community membership is required")

	def _post_to_payload(self, post: Any) -> dict[str, Any]:
		return {
			"id": post.id,
			"author_id": post.author_id,
			"community_id": post.community_id,
			"visibility": self._coerce_visibility(post.visibility),
			"title": post.title,
			"body": post.body,
			"created_at": post.created_at,
			"updated_at": post.updated_at,
			"is_deleted": post.is_deleted,
		}

	def _parse_uuid(self, value: UUID | str, *, label: str) -> UUID:
		if isinstance(value, UUID):
			return value

		try:
			return UUID(value)
		except (TypeError, ValueError) as exc:
			raise ValidationError(f"Invalid {label}") from exc

	def _parse_optional_uuid(self, value: UUID | str | None, *, label: str) -> UUID | None:
		if value is None:
			return None
		return self._parse_uuid(value, label=label)

	def _normalize_optional_uuid(self, value: Any, *, label: str) -> UUID | None:
		if value in (None, ""):
			return None
		return self._parse_uuid(value, label=label)

	def _normalize_required_text(self, value: Any, *, label: str) -> str:
		if not isinstance(value, str):
			raise ValidationError(f"{label.capitalize()} must be a string")
		normalized_value = value.strip()
		if not normalized_value:
			raise ValidationError(f"{label.capitalize()} must not be empty")
		return normalized_value

	def _normalize_optional_text(self, value: Any, *, label: str, max_length: int) -> str | None:
		if value is None:
			return None
		if not isinstance(value, str):
			raise ValidationError(f"{label.capitalize()} must be a string or null")
		normalized_value = value.strip()
		if not normalized_value:
			return None
		if len(normalized_value) > max_length:
			raise ValidationError(f"{label.capitalize()} must be at most {max_length} characters")
		return normalized_value

	def _normalize_visibility(self, value: Any) -> str:
		visibility = self._coerce_visibility(value)
		if visibility not in {"public", "private", "community"}:
			raise ValidationError("Visibility must be 'public', 'private', or 'community'")
		return visibility

	def _coerce_visibility(self, value: Any) -> str:
		if isinstance(value, str):
			return value

		coerced_value = getattr(value, "value", None)
		if isinstance(coerced_value, str):
			return coerced_value

		raise ValidationError("Invalid post visibility")

	def _normalize_limit(self, value: int) -> int:
		if value < 1 or value > 100:
			raise ValidationError("Limit must be between 1 and 100")
		return value

	def _normalize_offset(self, value: int) -> int:
		if value < 0:
			raise ValidationError("Offset must be greater than or equal to 0")
		return value


__all__ = ["CONTENT_POSTS_DELETE_PERMISSION", "ContentService"]
