from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.models.models import Post, PostVisibility


class ContentRepository:
	def __init__(self, session: AsyncSession) -> None:
		self._session = session

	async def create(self, data: dict[str, Any]) -> Post:
		post = Post(**data)
		self._session.add(post)
		await self._session.flush()
		return post

	async def get_by_id(self, post_id: UUID) -> Post | None:
		statement = select(Post).where(Post.id == post_id, Post.is_deleted.is_(False))
		return await self._session.scalar(statement)

	async def get_public_feed(self, limit: int, offset: int) -> list[Post]:
		statement = (
			select(Post)
			.where(
				Post.is_deleted.is_(False),
				Post.visibility == PostVisibility.PUBLIC,
			)
			.order_by(Post.created_at.desc())
			.limit(limit)
			.offset(offset)
		)
		return list((await self._session.scalars(statement)).all())

	async def get_user_posts(self, author_id: UUID, viewer_id: UUID | None) -> list[Post]:
		visibility_filters = [Post.visibility == PostVisibility.PUBLIC]
		if viewer_id == author_id:
			visibility_filters.append(Post.visibility == PostVisibility.PRIVATE)
			visibility_filters.append(Post.visibility == PostVisibility.COMMUNITY)
		else:
			visibility_filters.append(Post.visibility == PostVisibility.COMMUNITY)

		statement = (
			select(Post)
			.where(
				Post.is_deleted.is_(False),
				Post.author_id == author_id,
				or_(*visibility_filters),
			)
			.order_by(Post.created_at.desc())
		)
		return list((await self._session.scalars(statement)).all())

	async def get_community_posts(self, community_id: UUID, limit: int, offset: int) -> list[Post]:
		statement = (
			select(Post)
			.where(
				Post.is_deleted.is_(False),
				Post.community_id == community_id,
				Post.visibility == PostVisibility.COMMUNITY,
			)
			.order_by(Post.created_at.desc())
			.limit(limit)
			.offset(offset)
		)
		return list((await self._session.scalars(statement)).all())

	async def soft_delete(self, post_id: UUID) -> bool:
		post = await self.get_by_id(post_id)
		if post is None:
			return False

		post.is_deleted = True
		await self._session.flush()
		return True


__all__ = ["ContentRepository"]
