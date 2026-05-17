from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(sub: str, minutes: int, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {'sub': sub, 'iat': now, 'exp': now + timedelta(minutes=minutes)}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(sub: str) -> str:
    return create_token(sub, settings.access_token_minutes, {'typ': 'access'})


def create_refresh_token(sub: str) -> str:
    return create_token(sub, settings.refresh_token_days * 24 * 60, {'typ': 'refresh'})
