from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admins.models.models import Permission, Role, RolePermission
from app.shared.database.session import AsyncSessionLocal, engine


DEFAULT_PERMISSIONS: tuple[dict[str, str], ...] = (
	{
		"name": "admins.system_users.manage",
		"description": "Create, update, and deactivate system-user accounts.",
	},
	{
		"name": "admins.system_users.read",
		"description": "Read system-user account data.",
	},
	{
		"name": "admins.roles.manage",
		"description": "Create roles and assign or revoke roles for system users.",
	},
	{
		"name": "admins.permissions.manage",
		"description": "Create permissions and assign them to roles.",
	},
	{
		"name": "admins.system_permissions.read",
		"description": "Read the effective system permissions for a system user.",
	},
)

DEFAULT_ROLES: tuple[dict[str, str | tuple[str, ...]], ...] = (
	{
		"name": "super_admin",
		"description": "Full access to the admins boundary.",
		"permissions": tuple(permission["name"] for permission in DEFAULT_PERMISSIONS),
	},
)


async def _get_permission_by_name(session: AsyncSession, name: str) -> Permission | None:
	statement = select(Permission).where(Permission.name == name)
	return await session.scalar(statement)


async def _get_role_by_name(session: AsyncSession, name: str) -> Role | None:
	statement = select(Role).where(Role.name == name)
	return await session.scalar(statement)


async def _get_role_permission(
	session: AsyncSession,
	*,
	role_id: UUID,
	permission_id: UUID,
) -> RolePermission | None:
	statement = select(RolePermission).where(
		RolePermission.role_id == role_id,
		RolePermission.permission_id == permission_id,
	)
	return await session.scalar(statement)


async def seed_admins(session: AsyncSession) -> None:
	created_permissions = 0
	created_roles = 0
	created_role_permissions = 0

	permissions_by_name: dict[str, Permission] = {}
	for permission_seed in DEFAULT_PERMISSIONS:
		permission = await _get_permission_by_name(session, permission_seed["name"])
		if permission is None:
			permission = Permission(
				id=uuid4(),
				name=permission_seed["name"],
				description=permission_seed["description"],
			)
			session.add(permission)
			await session.flush()
			created_permissions += 1

		permissions_by_name[permission.name] = permission

	for role_seed in DEFAULT_ROLES:
		role = await _get_role_by_name(session, str(role_seed["name"]))
		if role is None:
			role = Role(
				id=uuid4(),
				name=str(role_seed["name"]),
				description=str(role_seed["description"]),
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
					RolePermission(
						role_id=role.id,
						permission_id=permission.id,
					)
				)
				created_role_permissions += 1

	print(
		"Seeded admins reference data "
		f"(permissions created: {created_permissions}, roles created: {created_roles}, "
		f"role permissions created: {created_role_permissions})."
	)


async def main() -> None:
	session = AsyncSessionLocal()
	try:
		await seed_admins(session)
		await session.commit()
	except Exception:
		await session.rollback()
		raise
	finally:
		await session.close()
		await engine.dispose()


if __name__ == "__main__":
	asyncio.run(main())