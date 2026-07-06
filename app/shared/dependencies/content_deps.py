from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.clients.communities_client import CommunitiesClient
from app.modules.content.public.facade import ContentFacade
from app.modules.content.repositories.repository import ContentRepository
from app.modules.content.services.service import ContentService
from app.shared.database.session import get_db
from app.shared.dependencies.communities_deps import get_community_facade


def get_content_repository(
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ContentRepository:
	return ContentRepository(db)


def get_content_communities_client(
	communities_facade=Depends(get_community_facade),
) -> CommunitiesClient:
	return CommunitiesClient(communities_facade)


def get_content_service(
	repo: Annotated[ContentRepository, Depends(get_content_repository)],
	communities_client: Annotated[CommunitiesClient, Depends(get_content_communities_client)],
) -> ContentService:
	return ContentService(repo, communities_client)


def get_content_facade(
	service: Annotated[ContentService, Depends(get_content_service)],
) -> ContentFacade:
	return ContentFacade(service)


__all__ = [
	"get_content_communities_client",
	"get_content_facade",
	"get_content_repository",
	"get_content_service",
]
