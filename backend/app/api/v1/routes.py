from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.middleware.rbac import current_user, optional_current_user, require_permission
from app.models.models import (
    AuditLog,
    Holiday,
    KnowledgeArticle,
    Ministry,
    MinistryTask,
    News,
    Role,
    RoleType,
    PrayerRequest,
    PrayerSupport,
    Sermon,
    User,
)
from app.schemas.auth import LoginIn, RegisterIn, TokenPair, TwoFAEnableIn, UserCreateIn, UserOut, UserPatchIn
from app.schemas.domain import (
    KnowledgeIn,
    KnowledgeOut,
    KnowledgePatch,
    MinistryIn,
    MinistryOut,
    MinistryPatch,
    NewsIn,
    NewsOut,
    NewsPatch,
    PrayerIn,
    PrayerModerateIn,
    PrayerOut,
    PrayerSupportIn,
    PresignedUrlOut,
    SermonIn,
    SermonOut,
    SermonPatch,
    TaskIn,
    TaskOut,
    TaskPatch,
    HolidayIn,
    HolidayOut,
    HolidayPatch,
)
from app.security.auth import create_access_token, create_refresh_token, hash_password, verify_password
from app.security.crypto import encrypt_text
from app.services.crud import create, delete_entity, get_or_404, list_by_stmt, update_entity, write_audit
from app.services.storage import presigned_download_url, presigned_upload_url

router = APIRouter()


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        twofa_enabled=user.twofa_enabled,
        roles=[str(role.name.value) for role in user.roles],
    )


async def _resolve_roles(db: AsyncSession, role_names: list[str]) -> list[Role]:
    if not role_names:
        role_names = ['member']
    try:
        role_types = [RoleType(role_name) for role_name in role_names]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='Unknown role in payload') from exc
    result = await db.execute(select(Role).where(Role.name.in_(role_types)))
    roles = result.scalars().all()
    if len(roles) != len(set(role_types)):
        raise HTTPException(status_code=400, detail='Unknown role in payload')
    return roles


@router.post('/auth/register')
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail='Email already exists')
    user = await create(
        db,
        User,
        {'email': payload.email, 'full_name': payload.full_name, 'password_hash': hash_password(payload.password)},
    )
    user.roles = await _resolve_roles(db, ['member'])
    await db.commit()
    await db.refresh(user, attribute_names=['roles'])
    user_data = {
        'id': str(user.id),
        'email': user.email,
        'fullName': user.full_name,
        'avatar': None,
        'roles': [str(role.name.value) for role in user.roles],
    }
    return {
        'accessToken': create_access_token(str(user.id)),
        'refreshToken': create_refresh_token(str(user.id)),
        'tokenType': 'bearer',
        'user': user_data,
    }


@router.post('/auth/login')
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    if not user.is_active:
        raise HTTPException(status_code=403, detail='User is disabled')
    user_data = {
        'id': str(user.id),
        'email': user.email,
        'fullName': user.full_name,
        'avatar': None,
        'roles': [str(role.name.value) for role in user.roles],
    }
    return {
        'accessToken': create_access_token(str(user.id)),
        'refreshToken': create_refresh_token(str(user.id)),
        'tokenType': 'bearer',
        'user': user_data,
    }


@router.get('/users/me', response_model=UserOut)
async def me(user: User = Depends(current_user)) -> UserOut:
    return _user_out(user)


@router.get('/roles', response_model=list[str], dependencies=[Depends(require_permission('users.manage'))])
async def list_roles() -> list[str]:
    return ['admin', 'editor', 'ministry_lead', 'staff', 'member']


@router.get('/users', response_model=list[UserOut], dependencies=[Depends(require_permission('users.manage'))])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[UserOut]:
    users = await list_by_stmt(
        db, select(User).options(selectinload(User.roles)).order_by(User.created_at.desc())
    )
    return [_user_out(user) for user in users]


@router.post('/users', response_model=UserOut, dependencies=[Depends(require_permission('users.manage'))])
async def create_user(payload: UserCreateIn, db: AsyncSession = Depends(get_db), actor: User = Depends(current_user)) -> UserOut:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail='Email already exists')
    user = await create(
        db,
        User,
        {
            'email': payload.email,
            'full_name': payload.full_name,
            'password_hash': hash_password(payload.password),
            'is_active': payload.is_active,
        },
    )
    user.roles = await _resolve_roles(db, payload.roles)
    await db.commit()
    await db.refresh(user)
    await write_audit(db, str(actor.id), 'create', 'users', str(user.id), payload.model_dump(exclude={'password'}))
    return _user_out(user)


@router.patch('/users/{user_id}', response_model=UserOut, dependencies=[Depends(require_permission('users.manage'))])
async def patch_user(
    user_id: str,
    payload: UserPatchIn,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(current_user),
) -> UserOut:
    try:
        user = await get_or_404(db, User, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    patch = payload.model_dump(exclude_none=True)
    if 'full_name' in patch:
        user.full_name = patch['full_name']
    if 'is_active' in patch:
        user.is_active = patch['is_active']
    if 'password' in patch:
        user.password_hash = hash_password(patch['password'])
    if 'roles' in patch:
        user.roles = await _resolve_roles(db, patch['roles'])
    await db.commit()
    await db.refresh(user)
    await write_audit(db, str(actor.id), 'update', 'users', str(user.id), payload.model_dump(exclude={'password'}))
    return _user_out(user)


@router.post('/users/me/2fa/enable', response_model=UserOut)
async def enable_2fa(payload: TwoFAEnableIn, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> UserOut:
    user.twofa_enabled = True
    user.twofa_secret_encrypted = encrypt_text(payload.secret)
    await db.commit()
    await write_audit(db, str(user.id), 'enable_2fa', 'users', str(user.id), {})
    return _user_out(user)


@router.post('/media/presign', response_model=PresignedUrlOut)
async def create_presigned_url(
    folder: str = Query(default='uploads'),
    filename: str = Query(default='file.bin'),
    user: User = Depends(current_user),
) -> PresignedUrlOut:
    key = f"{folder}/{user.id}/{uuid4()}-{filename}"
    return PresignedUrlOut(key=key, upload_url=presigned_upload_url(key), download_url=presigned_download_url(key))


@router.get('/sermons', response_model=list[SermonOut])
async def list_sermons(
    q: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[Sermon]:
    stmt = select(Sermon)
    if q:
        stmt = stmt.where(Sermon.title.ilike(f'%{q}%'))
    if tag:
        stmt = stmt.where(Sermon.tags.contains([tag]))
    return await list_by_stmt(db, stmt.order_by(Sermon.preached_on.desc()))


@router.get('/sermons/{sermon_id}', response_model=SermonOut)
async def get_sermon(sermon_id: str, db: AsyncSession = Depends(get_db)) -> Sermon:
    try:
        return await get_or_404(db, Sermon, sermon_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc


@router.post('/sermons', response_model=SermonOut, dependencies=[Depends(require_permission('sermons.write'))])
async def create_sermon(payload: SermonIn, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> Sermon:
    obj = await create(db, Sermon, {**payload.model_dump(), 'author_id': user.id})
    await write_audit(db, str(user.id), 'create', 'sermons', str(obj.id), payload.model_dump())
    return obj


@router.patch('/sermons/{sermon_id}', response_model=SermonOut, dependencies=[Depends(require_permission('sermons.write'))])
async def patch_sermon(sermon_id: str, payload: SermonPatch, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> Sermon:
    try:
        obj = await get_or_404(db, Sermon, sermon_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    obj = await update_entity(db, obj, payload.model_dump(exclude_none=True))
    await write_audit(db, str(user.id), 'update', 'sermons', str(obj.id), payload.model_dump(exclude_none=True))
    return obj


@router.delete('/sermons/{sermon_id}', dependencies=[Depends(require_permission('sermons.write'))])
async def remove_sermon(sermon_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    try:
        obj = await get_or_404(db, Sermon, sermon_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    await delete_entity(db, obj)
    await write_audit(db, str(user.id), 'delete', 'sermons', sermon_id, {})
    return {'status': 'deleted'}


@router.get('/news', response_model=list[NewsOut])
async def list_news(
    q: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[News]:
    stmt = select(News)
    if q:
        stmt = stmt.where(News.title.ilike(f'%{q}%'))
    return await list_by_stmt(db, stmt.order_by(News.publish_at.desc()))


@router.post('/news', response_model=NewsOut, dependencies=[Depends(require_permission('news.write'))])
async def create_news(payload: NewsIn, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> News:
    obj = await create(db, News, payload.model_dump())
    await write_audit(db, str(user.id), 'create', 'news', str(obj.id), payload.model_dump())
    return obj


@router.patch('/news/{news_id}', response_model=NewsOut, dependencies=[Depends(require_permission('news.write'))])
async def patch_news(news_id: str, payload: NewsPatch, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> News:
    try:
        obj = await get_or_404(db, News, news_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    obj = await update_entity(db, obj, payload.model_dump(exclude_none=True))
    await write_audit(db, str(user.id), 'update', 'news', str(obj.id), payload.model_dump(exclude_none=True))
    return obj


@router.delete('/news/{news_id}', dependencies=[Depends(require_permission('news.write'))])
async def remove_news(news_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    try:
        obj = await get_or_404(db, News, news_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    await delete_entity(db, obj)
    await write_audit(db, str(user.id), 'delete', 'news', news_id, {})
    return {'status': 'deleted'}


@router.get('/prayers', response_model=list[PrayerOut])
async def list_prayers(
    status: str | None = Query(default=None),
    public_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
) -> list[PrayerRequest]:
    stmt = select(PrayerRequest)
    if status:
        stmt = stmt.where(PrayerRequest.status == status)
    if public_only:
        stmt = stmt.where(PrayerRequest.status == 'active', PrayerRequest.is_moderated.is_(True))
    return await list_by_stmt(db, stmt.order_by(PrayerRequest.created_at.desc()))


@router.post('/prayers', response_model=PrayerOut)
async def create_prayer(
    payload: PrayerIn,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
) -> PrayerRequest:
    obj = await create(db, PrayerRequest, {**payload.model_dump(), 'author_id': user.id if user else None})
    await write_audit(db, str(user.id) if user else None, 'create', 'prayers', str(obj.id), payload.model_dump())
    return obj


@router.post('/prayers/{prayer_id}/support', response_model=PrayerOut)
async def support_prayer(prayer_id: str, payload: PrayerSupportIn, db: AsyncSession = Depends(get_db)) -> PrayerRequest:
    try:
        prayer = await get_or_404(db, PrayerRequest, prayer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    existing = await db.execute(
        select(PrayerSupport).where(
            PrayerSupport.prayer_id == prayer.id,
            PrayerSupport.supporter_fingerprint == payload.fingerprint,
        )
    )
    if existing.scalar_one_or_none() is None:
        db.add(PrayerSupport(prayer_id=prayer.id, supporter_fingerprint=payload.fingerprint))
        prayer.support_count += 1
        await db.commit()
        await db.refresh(prayer)
    return prayer


@router.patch('/prayers/{prayer_id}', response_model=PrayerOut, dependencies=[Depends(require_permission('prayers.moderate'))])
async def moderate_prayer(prayer_id: str, payload: PrayerModerateIn, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> PrayerRequest:
    try:
        prayer = await get_or_404(db, PrayerRequest, prayer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    prayer = await update_entity(db, prayer, payload.model_dump())
    await write_audit(db, str(user.id), 'moderate', 'prayers', str(prayer.id), payload.model_dump())
    return prayer


@router.get('/ministries', response_model=list[MinistryOut])
async def list_ministries(db: AsyncSession = Depends(get_db)) -> list[Ministry]:
    return await list_by_stmt(db, select(Ministry).order_by(Ministry.name.asc()))


@router.post('/ministries', response_model=MinistryOut, dependencies=[Depends(require_permission('ministries.write'))])
async def create_ministry(payload: MinistryIn, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> Ministry:
    obj = await create(db, Ministry, payload.model_dump())
    await write_audit(db, str(user.id), 'create', 'ministries', str(obj.id), payload.model_dump())
    return obj


@router.patch('/ministries/{ministry_id}', response_model=MinistryOut, dependencies=[Depends(require_permission('ministries.write'))])
async def patch_ministry(ministry_id: str, payload: MinistryPatch, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> Ministry:
    try:
        obj = await get_or_404(db, Ministry, ministry_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    obj = await update_entity(db, obj, payload.model_dump(exclude_none=True))
    await write_audit(db, str(user.id), 'update', 'ministries', str(obj.id), payload.model_dump(exclude_none=True))
    return obj


@router.delete('/ministries/{ministry_id}', dependencies=[Depends(require_permission('ministries.write'))])
async def remove_ministry(ministry_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    try:
        obj = await get_or_404(db, Ministry, ministry_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    await delete_entity(db, obj)
    await write_audit(db, str(user.id), 'delete', 'ministries', ministry_id, {})
    return {'status': 'deleted'}


@router.get('/tasks', response_model=list[TaskOut])
async def list_tasks(
    ministry_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[MinistryTask]:
    stmt = select(MinistryTask)
    if ministry_id:
        stmt = stmt.where(MinistryTask.ministry_id == ministry_id)
    if status:
        stmt = stmt.where(MinistryTask.status == status)
    return await list_by_stmt(db, stmt.order_by(MinistryTask.deadline.asc()))


@router.post('/tasks', response_model=TaskOut, dependencies=[Depends(require_permission('tasks.write'))])
async def create_task(payload: TaskIn, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> MinistryTask:
    obj = await create(db, MinistryTask, payload.model_dump())
    await write_audit(db, str(user.id), 'create', 'tasks', str(obj.id), payload.model_dump())
    return obj


@router.patch('/tasks/{task_id}', response_model=TaskOut, dependencies=[Depends(require_permission('tasks.write'))])
async def patch_task(task_id: str, payload: TaskPatch, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> MinistryTask:
    try:
        obj = await get_or_404(db, MinistryTask, task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    obj = await update_entity(db, obj, payload.model_dump(exclude_none=True))
    await write_audit(db, str(user.id), 'update', 'tasks', str(obj.id), payload.model_dump(exclude_none=True))
    return obj


@router.delete('/tasks/{task_id}', dependencies=[Depends(require_permission('tasks.write'))])
async def remove_task(task_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    try:
        obj = await get_or_404(db, MinistryTask, task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    await delete_entity(db, obj)
    await write_audit(db, str(user.id), 'delete', 'tasks', task_id, {})
    return {'status': 'deleted'}


@router.get('/knowledge', response_model=list[KnowledgeOut])
async def list_knowledge(q: str | None = Query(default=None), db: AsyncSession = Depends(get_db)) -> list[KnowledgeArticle]:
    stmt = select(KnowledgeArticle)
    if q:
        stmt = stmt.where(KnowledgeArticle.title.ilike(f'%{q}%'))
    return await list_by_stmt(db, stmt.order_by(KnowledgeArticle.updated_at.desc()))


@router.post('/knowledge', response_model=KnowledgeOut, dependencies=[Depends(require_permission('knowledge.write'))])
async def create_knowledge(payload: KnowledgeIn, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> KnowledgeArticle:
    obj = await create(db, KnowledgeArticle, payload.model_dump())
    await write_audit(db, str(user.id), 'create', 'knowledge', str(obj.id), payload.model_dump())
    return obj


@router.patch('/knowledge/{article_id}', response_model=KnowledgeOut, dependencies=[Depends(require_permission('knowledge.write'))])
async def patch_knowledge(article_id: str, payload: KnowledgePatch, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> KnowledgeArticle:
    try:
        obj = await get_or_404(db, KnowledgeArticle, article_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    patch = payload.model_dump(exclude_none=True)
    if patch.get('body_markdown'):
        patch['version'] = obj.version + 1
    obj = await update_entity(db, obj, patch)
    await write_audit(db, str(user.id), 'update', 'knowledge', str(obj.id), patch)
    return obj


@router.delete('/knowledge/{article_id}', dependencies=[Depends(require_permission('knowledge.write'))])
async def remove_knowledge(article_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    try:
        obj = await get_or_404(db, KnowledgeArticle, article_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    await delete_entity(db, obj)
    await write_audit(db, str(user.id), 'delete', 'knowledge', article_id, {})
    return {'status': 'deleted'}


@router.get('/holidays', response_model=list[HolidayOut])
async def list_holidays(
    month: int | None = Query(default=None, ge=1, le=12),
    public_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
) -> list[Holiday]:
    stmt = select(Holiday)
    if month is not None:
        stmt = stmt.where(extract('month', Holiday.event_date) == month)
    if public_only:
        stmt = stmt.where(Holiday.is_public.is_(True))
    return await list_by_stmt(db, stmt.order_by(Holiday.event_date.asc()))


@router.post('/holidays', response_model=HolidayOut, dependencies=[Depends(require_permission('holidays.write'))])
async def create_holiday(payload: HolidayIn, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> Holiday:
    obj = await create(db, Holiday, payload.model_dump())
    await write_audit(db, str(user.id), 'create', 'holidays', str(obj.id), payload.model_dump())
    return obj


@router.patch('/holidays/{holiday_id}', response_model=HolidayOut, dependencies=[Depends(require_permission('holidays.write'))])
async def patch_holiday(holiday_id: str, payload: HolidayPatch, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> Holiday:
    try:
        obj = await get_or_404(db, Holiday, holiday_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    obj = await update_entity(db, obj, payload.model_dump(exclude_none=True))
    await write_audit(db, str(user.id), 'update', 'holidays', str(obj.id), payload.model_dump(exclude_none=True))
    return obj


@router.delete('/holidays/{holiday_id}', dependencies=[Depends(require_permission('holidays.write'))])
async def remove_holiday(holiday_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    try:
        obj = await get_or_404(db, Holiday, holiday_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    await delete_entity(db, obj)
    await write_audit(db, str(user.id), 'delete', 'holidays', holiday_id, {})
    return {'status': 'deleted'}


@router.get('/audit-logs', response_model=list[dict], dependencies=[Depends(require_permission('audit.read'))])
async def list_audit_logs(limit: int = Query(default=100, le=500), db: AsyncSession = Depends(get_db)) -> list[dict]:
    logs = await list_by_stmt(db, select(AuditLog).order_by(AuditLog.id.desc()).limit(limit))
    return [
        {
            'id': log.id,
            'action': log.action,
            'entity_type': log.entity_type,
            'entity_id': log.entity_id,
            'payload': log.payload,
            'created_at': log.created_at,
        }
        for log in logs
    ]


@router.delete('/users/{user_id}', dependencies=[Depends(require_permission('users.delete'))])
async def anonymize_user(user_id: str, db: AsyncSession = Depends(get_db), actor: User = Depends(current_user)) -> dict[str, str]:
    try:
        user = await get_or_404(db, User, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not found') from exc
    user.email = f'anonymized-{user.id}@deleted.local'
    user.full_name = 'Deleted User'
    user.password_hash = hash_password('disabled-account-password')
    user.phone_encrypted = encrypt_text('deleted')
    user.twofa_secret_encrypted = encrypt_text('deleted')
    user.is_active = False
    await db.commit()
    await write_audit(db, str(actor.id), 'anonymize', 'users', str(user.id), {})
    return {'status': 'anonymized'}
