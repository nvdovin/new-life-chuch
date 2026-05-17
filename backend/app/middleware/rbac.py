from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.models import Role, User

bearer = HTTPBearer(auto_error=False)


async def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing token')
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get('sub')
    except JWTError as exc:
        raise HTTPException(status_code=401, detail='Invalid token') from exc

    stmt = select(User).options(selectinload(User.roles).selectinload(Role.permissions)).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail='User not active')
    return user


async def optional_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not creds:
        return None
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get('sub')
    except JWTError:
        return None
    stmt = select(User).options(selectinload(User.roles).selectinload(Role.permissions)).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        return None
    return user


def require_permission(permission_code: str) -> Callable:
    async def checker(user: User = Depends(current_user)) -> User:
        permissions = {perm.code for role in user.roles for perm in role.permissions}
        if permission_code not in permissions:
            raise HTTPException(status_code=403, detail='Permission denied')
        return user

    return checker
