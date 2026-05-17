from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.models import Permission, Role, RoleType

DEFAULT_PERMISSIONS = [
    'sermons.write', 'news.write', 'prayers.read', 'prayers.moderate',
    'ministries.write', 'tasks.write', 'knowledge.write', 'audit.read',
    'users.delete', 'holidays.write'
]

ROLE_PERMISSIONS: dict[RoleType, list[str]] = {
    RoleType.ADMIN: DEFAULT_PERMISSIONS,
    RoleType.EDITOR: ['sermons.write', 'news.write', 'prayers.read', 'prayers.moderate', 'holidays.write'],
    RoleType.MINISTRY_LEAD: ['ministries.write', 'tasks.write', 'knowledge.write', 'prayers.read'],
    RoleType.STAFF: ['tasks.write', 'knowledge.write', 'prayers.read'],
    RoleType.MEMBER: ['prayers.read'],
}


async def seed_rbac() -> None:
    async with SessionLocal() as session:
        for code in DEFAULT_PERMISSIONS:
            found = await session.execute(select(Permission).where(Permission.code == code))
            if found.scalar_one_or_none() is None:
                session.add(Permission(code=code, description=code))
        await session.commit()

        perm_rows = await session.execute(select(Permission))
        perms = {p.code: p for p in perm_rows.scalars().all()}

        for role_type, role_perm_codes in ROLE_PERMISSIONS.items():
            role_row = await session.execute(select(Role).where(Role.name == role_type))
            role = role_row.scalar_one_or_none()
            if role is None:
                role = Role(name=role_type)
                session.add(role)
                await session.flush()
            role.permissions = [perms[c] for c in role_perm_codes if c in perms]
        await session.commit()


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_rbac()
