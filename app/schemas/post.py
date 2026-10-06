from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl

from app.models.post import PostStatus


class PostCreate(BaseModel):
    title: str
    slug: str
    excerpt: str | None = None
    content: str
    status: PostStatus = PostStatus.DRAFT
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    featured: bool = False
    featured_media_id: UUID | None = None
    author_id: UUID
    category_id: UUID
    event_id: UUID | None = None
    video_url: HttpUrl | None = None


class PostUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    excerpt: str | None = None
    content: str | None = None
    status: PostStatus | None = None
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    featured: bool | None = None
    featured_media_id: UUID | None = None
    author_id: UUID | None = None
    category_id: UUID | None = None
    event_id: UUID | None = None
    video_url: HttpUrl | None = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    excerpt: str | None
    content: str
    status: PostStatus
    scheduled_at: datetime | None
    published_at: datetime | None
    featured: bool
    featured_media_id: UUID | None
    author_id: UUID
    category_id: UUID
    event_id: UUID | None
    video_url: HttpUrl | None
    created_at: datetime
    updated_at: datetime
