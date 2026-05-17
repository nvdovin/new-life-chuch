import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoleType(str, enum.Enum):
    ADMIN = 'admin'
    EDITOR = 'editor'
    MINISTRY_LEAD = 'ministry_lead'
    STAFF = 'staff'
    MEMBER = 'member'


class PrayerStatus(str, enum.Enum):
    ACTIVE = 'active'
    CLOSED = 'closed'


class Priority(str, enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    phone_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    twofa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    twofa_secret_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    roles: Mapped[list['Role']] = relationship(secondary=user_roles, back_populates='users')


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[RoleType] = mapped_column(Enum(RoleType), unique=True)
    users: Mapped[list[User]] = relationship(secondary=user_roles, back_populates='roles')
    permissions: Mapped[list['Permission']] = relationship(
        secondary=role_permissions, back_populates='roles'
    )


class Permission(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255))
    roles: Mapped[list[Role]] = relationship(secondary=role_permissions, back_populates='permissions')


class Sermon(Base, TimestampMixin):
    __tablename__ = 'sermons'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    preached_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    audio_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    __table_args__ = (Index('ix_sermons_title_date', 'title', 'preached_on'),)


class News(Base, TimestampMixin):
    __tablename__ = 'news'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True)
    body: Mapped[str] = mapped_column(Text)
    media_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.MEDIUM)
    publish_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    birthday_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birthday_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class PrayerRequest(Base, TimestampMixin):
    __tablename__ = 'prayer_requests'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[PrayerStatus] = mapped_column(Enum(PrayerStatus), default=PrayerStatus.ACTIVE, index=True)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=False)
    support_count: Mapped[int] = mapped_column(Integer, default=0)


class PrayerSupport(Base, TimestampMixin):
    __tablename__ = 'prayer_supports'
    __table_args__ = (
        UniqueConstraint('prayer_id', 'supporter_fingerprint', name='uq_prayer_support'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prayer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('prayer_requests.id', ondelete='CASCADE'), index=True)
    supporter_fingerprint: Mapped[str] = mapped_column(String(255), index=True)


class Holiday(Base, TimestampMixin):
    __tablename__ = 'holidays'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_date: Mapped[date] = mapped_column(Date, index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)


class Ministry(Base, TimestampMixin):
    __tablename__ = 'ministries'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


task_assignees = Table(
    'task_assignees',
    Base.metadata,
    Column('task_id', ForeignKey('ministry_tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)

task_watchers = Table(
    'task_watchers',
    Base.metadata,
    Column('task_id', ForeignKey('ministry_tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)


class MinistryTask(Base, TimestampMixin):
    __tablename__ = 'ministry_tasks'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ministry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('ministries.id', ondelete='RESTRICT'), index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('ministry_tasks.id', ondelete='SET NULL'), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='todo', index=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.MEDIUM, index=True)
    depth: Mapped[int] = mapped_column(Integer, default=1)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __table_args__ = (
        CheckConstraint('depth >= 1 AND depth <= 3', name='ck_task_depth'),
        Index('ix_task_ministry_status', 'ministry_id', 'status'),
    )


class KnowledgeArticle(Base, TimestampMixin):
    __tablename__ = 'knowledge_articles'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('knowledge_articles.id', ondelete='SET NULL'), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), index=True)
    body_markdown: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    __table_args__ = (UniqueConstraint('token_hash', name='uq_refresh_token_hash'),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
