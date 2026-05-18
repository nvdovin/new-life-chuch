from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.models import Permission, Role, RoleType, User, role_permissions
from app.security.auth import hash_password

DEFAULT_PERMISSIONS = [
    'sermons.write', 'news.write', 'prayers.read', 'prayers.moderate',
    'ministries.write', 'tasks.write', 'knowledge.write', 'audit.read',
    'users.delete', 'holidays.write', 'users.manage'
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
        # Create all permissions first
        for code in DEFAULT_PERMISSIONS:
            found = await session.execute(select(Permission).where(Permission.code == code))
            if found.scalar_one_or_none() is None:
                session.add(Permission(code=code, description=code))
        await session.commit()

        perm_rows = await session.execute(select(Permission))
        perms = {p.code: p for p in perm_rows.scalars().all()}

        # Create all roles - CRITICAL: Ensure ALL roles exist, especially 'member'
        for role_type, role_perm_codes in ROLE_PERMISSIONS.items():
            role_row = await session.execute(select(Role).where(Role.name == role_type))
            role = role_row.scalar_one_or_none()
            if role is None:
                role = Role(name=role_type)
                session.add(role)
                await session.flush()
                print(f"Created role: {role_type.value}")
            else:
                print(f"Role already exists: {role_type.value}")
            
            # Update role permissions
            await session.execute(delete(role_permissions).where(role_permissions.c.role_id == role.id))
            if role_perm_codes:
                await session.execute(
                    role_permissions.insert(),
                    [
                        {'role_id': role.id, 'permission_id': perms[code].id}
                        for code in role_perm_codes
                        if code in perms
                    ],
                )

        # Create admin user if not exists
        admin_row = await session.execute(select(Role).where(Role.name == RoleType.ADMIN))
        admin_role = admin_row.scalar_one()
        admin_user_row = await session.execute(
            select(User).options(selectinload(User.roles)).where(User.email == settings.bootstrap_admin_email)
        )
        admin_user = admin_user_row.scalar_one_or_none()
        if admin_user is None:
            admin_user = User(
                email=settings.bootstrap_admin_email,
                full_name=settings.bootstrap_admin_full_name,
                password_hash=hash_password(settings.bootstrap_admin_password),
                is_active=True,
            )
            admin_user.roles = [admin_role]
            session.add(admin_user)
            print(f"Created admin user: {settings.bootstrap_admin_email}")
        elif admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)
        await session.commit()
        print("RBAC seeding completed successfully")


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_rbac()
