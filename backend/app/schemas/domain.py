from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.models import PrayerStatus, Priority
from app.schemas.common import ORMModel


class SermonIn(BaseModel):
    title: str
    body: str | None = None
    preached_on: datetime
    audio_url: str | None = None
    video_url: str | None = None
    external_url: str | None = None
    transcript: str | None = None
    tags: list[str] = Field(default_factory=list)


class SermonPatch(BaseModel):
    title: str | None = None
    body: str | None = None
    preached_on: datetime | None = None
    audio_url: str | None = None
    video_url: str | None = None
    external_url: str | None = None
    transcript: str | None = None
    tags: list[str] | None = None


class SermonOut(ORMModel, SermonIn):
    id: UUID


class NewsIn(BaseModel):
    title: str
    body: str
    media_url: str | None = None
    priority: Priority = Priority.MEDIUM
    publish_at: datetime
    birthday_person: str | None = None
    birthday_date: date | None = None


class NewsPatch(BaseModel):
    title: str | None = None
    body: str | None = None
    media_url: str | None = None
    priority: Priority | None = None
    publish_at: datetime | None = None
    birthday_person: str | None = None
    birthday_date: date | None = None


class NewsOut(ORMModel, NewsIn):
    id: UUID


class PrayerIn(BaseModel):
    is_anonymous: bool = False
    category: str
    content: str = Field(min_length=10)


class PrayerModerateIn(BaseModel):
    status: PrayerStatus
    is_moderated: bool = True


class PrayerOut(ORMModel):
    id: UUID
    author_id: UUID | None
    is_anonymous: bool
    category: str
    content: str
    status: PrayerStatus
    is_moderated: bool
    support_count: int


class PrayerSupportIn(BaseModel):
    fingerprint: str = Field(min_length=8, max_length=255)


class MinistryIn(BaseModel):
    name: str
    description: str | None = None


class MinistryPatch(BaseModel):
    name: str | None = None
    description: str | None = None


class MinistryOut(ORMModel, MinistryIn):
    id: UUID


class TaskIn(BaseModel):
    ministry_id: UUID
    parent_id: UUID | None = None
    title: str
    description: str | None = None
    status: Literal['todo', 'in_progress', 'done'] = 'todo'
    priority: Priority = Priority.MEDIUM
    depth: int = Field(ge=1, le=3, default=1)
    deadline: datetime | None = None


class TaskPatch(BaseModel):
    parent_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    status: Literal['todo', 'in_progress', 'done'] | None = None
    priority: Priority | None = None
    depth: int | None = Field(default=None, ge=1, le=3)
    deadline: datetime | None = None


class TaskOut(ORMModel, TaskIn):
    id: UUID


class KnowledgeIn(BaseModel):
    parent_id: UUID | None = None
    title: str
    body_markdown: str
    tags: list[str] = Field(default_factory=list)


class KnowledgePatch(BaseModel):
    parent_id: UUID | None = None
    title: str | None = None
    body_markdown: str | None = None
    tags: list[str] | None = None


class KnowledgeOut(ORMModel, KnowledgeIn):
    id: UUID
    version: int


class PresignedUrlOut(BaseModel):
    key: str
    upload_url: str
    download_url: str


class HolidayIn(BaseModel):
    title: str
    description: str | None = None
    event_date: date
    is_public: bool = True


class HolidayPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    event_date: date | None = None
    is_public: bool | None = None


class HolidayOut(ORMModel, HolidayIn):
    id: UUID
