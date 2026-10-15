from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

class CommunityProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=120)
    biography: str | None = None
    profile_media_id: UUID | None = None
    is_published: bool = False
    display_order: int = 0

    @field_validator("name", "category", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class CommunityProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=120)
    biography: str | None = None
    profile_media_id: UUID | None = None
    is_published: bool | None = None
    display_order: int | None = None

    @field_validator("name", "category", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class CommunityProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: str
    biography: str | None
    profile_media_id: UUID | None
    profile_media_url: str | None
    is_published: bool
    display_order: int
    created_at: datetime
    updated_at: datetime


class PublicCommunityProfileResponse(BaseModel):
    id: UUID
    name: str
    category: str
    biography: str | None
    profile_media_id: UUID | None
    profile_media_url: str | None


class CommunityProfileOrderRequest(BaseModel):
    profile_ids: list[UUID]
