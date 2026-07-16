from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


def _schema_metadata(schema_name: str) -> MetaData:
	return MetaData(schema=schema_name)


class UsersBase(AsyncAttrs, DeclarativeBase):
	__abstract__ = True
	metadata = _schema_metadata("users")


class AdminsBase(AsyncAttrs, DeclarativeBase):
	__abstract__ = True
	metadata = _schema_metadata("admins")


class SocialGraphBase(AsyncAttrs, DeclarativeBase):
	__abstract__ = True
	metadata = _schema_metadata("social_graph")


class CommunitiesBase(AsyncAttrs, DeclarativeBase):
	__abstract__ = True
	metadata = _schema_metadata("communities")


class ContentBase(AsyncAttrs, DeclarativeBase):
	__abstract__ = True
	metadata = _schema_metadata("content")


class NotificationsBase(AsyncAttrs, DeclarativeBase):
	__abstract__ = True
	metadata = _schema_metadata("notifications")


SCHEMA_NAMES: tuple[str, ...] = (
	"users",
	"admins",
	"social_graph",
	"communities",
	"content",
	"notifications",
)

ALL_METADATA: tuple[MetaData, ...] = (
	UsersBase.metadata,
	AdminsBase.metadata,
	SocialGraphBase.metadata,
	CommunitiesBase.metadata,
	ContentBase.metadata,
	NotificationsBase.metadata,
)


__all__ = [
	"ALL_METADATA",
	"AdminsBase",
	"CommunitiesBase",
	"ContentBase",
	"NotificationsBase",
	"SCHEMA_NAMES",
	"SocialGraphBase",
	"UsersBase",
]
