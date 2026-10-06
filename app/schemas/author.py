from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuthorCreate(BaseModel):
    name: str
    biography: str | None = None
    profile_media_id: UUID | None = None


class AuthorUpdate(BaseModel):
    name: str | None = None
    biography: str | None = None
    profile_media_id: UUID | None = None


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    biography: str | None
    profile_media_id: UUID | None
    created_at: datetime
    updated_at: datetime
