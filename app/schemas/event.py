from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.event import EventStatus
from app.schemas.gallery import GalleryImageResponse

class EventCreate(BaseModel):
    title: str
    slug: str
    description: str
    start_at: datetime
    end_at: datetime | None = None
    location: str | None = None
    status: EventStatus = EventStatus.DRAFT
    featured_media_id: UUID | None = None


class EventUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = None
    status: EventStatus | None = None
    featured_media_id: UUID | None = None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    description: str
    start_at: datetime
    end_at: datetime | None
    location: str | None
    status: EventStatus
    featured_media_id: UUID | None
    featured_media_url: str | None = None
    gallery_images: list[GalleryImageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
