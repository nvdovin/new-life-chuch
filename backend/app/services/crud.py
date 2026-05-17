from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuditLog

ModelType = TypeVar('ModelType')


async def create(db: AsyncSession, model_cls: type[ModelType], payload: dict[str, Any]) -> ModelType:
    obj = model_cls(**payload)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_or_404(db: AsyncSession, model_cls: type[ModelType], entity_id: Any) -> ModelType:
    obj = await db.get(model_cls, entity_id)
    if obj is None:
        raise ValueError('Entity not found')
    return obj


async def list_by_stmt(db: AsyncSession, stmt: Select[tuple[ModelType]]) -> list[ModelType]:
    rows = await db.execute(stmt)
    return list(rows.scalars().all())


async def list_all(db: AsyncSession, model_cls: type[ModelType]) -> list[ModelType]:
    return await list_by_stmt(db, select(model_cls))


async def update_entity(db: AsyncSession, obj: ModelType, payload: dict[str, Any]) -> ModelType:
    for k, v in payload.items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_entity(db: AsyncSession, obj: ModelType) -> None:
    await db.delete(obj)
    await db.commit()


async def write_audit(
    db: AsyncSession,
    actor_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any],
) -> None:
    log = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload={**payload, 'at': datetime.utcnow().isoformat()},
    )
    db.add(log)
    await db.commit()
