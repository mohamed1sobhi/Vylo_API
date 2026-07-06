from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.communities.models.models import CommunityPermission, CommunityRole, CommunityRolePermission
from app.shared.database.session import AsyncSessionLocal, engine


DEFAULT_PERMISSIONS: tuple[dict[str, str], ...] = (
	{
		"name": "communities.members.manage",
	},
	{
		"name": "communities.roles.read",
	},
)

DEFAULT_ROLES: tuple[dict[str, str | tuple[str, ...]], ...] = (
	{
		"name": "owner",
		"permissions": tuple(permission["name"] for permission in DEFAULT_PERMISSIONS),
	},
	{
		"name": "member",
		"permissions": ("communities.roles.read",),
	},
)


async def _get_permission_by_name(session: AsyncSession, name: str) -> CommunityPermission | None:
	statement = select(CommunityPermission).where(CommunityPermission.name == name)
	return await session.scalar(statement)


async def _get_role_by_name(session: AsyncSession, name: str) -> CommunityRole | None:
	statement = select(CommunityRole).where(CommunityRole.name == name)
	return await session.scalar(statement)


async def _get_role_permission(
	session: AsyncSession,
	*,
	role_id: UUID,
	permission_id: UUID,
) -> CommunityRolePermission | None:
	statement = select(CommunityRolePermission).where(
		CommunityRolePermission.role_id == role_id,
		CommunityRolePermission.permission_id == permission_id,
	)
	return await session.scalar(statement)


async def seed_communities(session: AsyncSession) -> None:
	created_permissions = 0
	created_roles = 0
	created_role_permissions = 0

	permissions_by_name: dict[str, CommunityPermission] = {}
	for permission_seed in DEFAULT_PERMISSIONS:
		permission = await _get_permission_by_name(session, permission_seed["name"])
		if permission is None:
			permission = CommunityPermission(
				id=uuid4(),
				name=permission_seed["name"],
			)
			session.add(permission)
			await session.flush()
			created_permissions += 1

		permissions_by_name[permission.name] = permission

	for role_seed in DEFAULT_ROLES:
		role = await _get_role_by_name(session, str(role_seed["name"]))
		if role is None:
			role = CommunityRole(
				id=uuid4(),
				name=str(role_seed["name"]),
			)
			session.add(role)
			await session.flush()
			created_roles += 1

		for permission_name in role_seed["permissions"]:
			permission = permissions_by_name[permission_name]
			role_permission = await _get_role_permission(
				session,
				role_id=role.id,
				permission_id=permission.id,
			)
			if role_permission is None:
				session.add(
					CommunityRolePermission(
						role_id=role.id,
						permission_id=permission.id,
					)
				)
				created_role_permissions += 1

	print(
		"Seeded communities reference data "
		f"(permissions created: {created_permissions}, roles created: {created_roles}, "
		f"role permissions created: {created_role_permissions})."
	)


async def main() -> None:
	session = AsyncSessionLocal()
	try:
		await seed_communities(session)
		await session.commit()
	except Exception:
		await session.rollback()
		raise
	finally:
		await session.close()
		await engine.dispose()


if __name__ == "__main__":
	asyncio.run(main())