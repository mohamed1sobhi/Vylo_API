from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models.models import Notification


class NotificationRepository:
	def __init__(self, session: AsyncSession) -> None:
		self._session = session

	async def create(self, recipient_id: UUID, type: str, payload: dict[str, Any]) -> Notification:
		notification = Notification(
			id=uuid4(),
			recipient_id=recipient_id,
			type=type,
			payload=payload,
			is_read=False,
		)
		self._session.add(notification)
		await self._session.flush()
		return notification

	async def get_for_user(self, user_id: UUID, limit: int, offset: int) -> list[Notification]:
		statement = (
			select(Notification)
			.where(Notification.recipient_id == user_id)
			.order_by(Notification.created_at.desc())
			.limit(limit)
			.offset(offset)
		)
		return list((await self._session.scalars(statement)).all())

	async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification | None:
		statement = select(Notification).where(
			Notification.id == notification_id,
			Notification.recipient_id == user_id,
		)
		notification = await self._session.scalar(statement)
		if notification is None:
			return None

		notification.is_read = True
		await self._session.flush()
		return notification

	async def mark_all_read(self, user_id: UUID) -> None:
		statement = (
			update(Notification)
			.where(Notification.recipient_id == user_id, Notification.is_read.is_(False))
			.values(is_read=True)
		)
		await self._session.execute(statement)
		await self._session.flush()

	async def commit(self) -> None:
		await self._session.commit()

	async def rollback(self) -> None:
		await self._session.rollback()


__all__ = ["NotificationRepository"]
