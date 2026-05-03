from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.public.facade import UserFacade
from app.modules.users.repositories.repository import UserRepository
from app.modules.users.services.service import UserService
from app.shared.database.session import get_db


def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
	return UserRepository(db)


def get_user_service(
	repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
	return UserService(repo)


def get_user_facade(
	service: Annotated[UserService, Depends(get_user_service)],
) -> UserFacade:
	return UserFacade(service)


__all__ = ["get_user_facade", "get_user_repository", "get_user_service"]