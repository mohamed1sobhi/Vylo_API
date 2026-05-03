from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admins.public.facade import AdminFacade
from app.modules.admins.repositories.repository import AdminRepository
from app.modules.admins.services.service import AdminService
from app.shared.database.session import get_db


def get_admin_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AdminRepository:
	return AdminRepository(db)


def get_admin_service(
	repo: Annotated[AdminRepository, Depends(get_admin_repository)],
) -> AdminService:
	return AdminService(repo)


def get_admin_facade(
	service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminFacade:
	return AdminFacade(service)


__all__ = ["get_admin_facade", "get_admin_repository", "get_admin_service"]