from uuid import UUID

from pydantic import BaseModel, Field


class GalleryImageResponse(BaseModel):
    media_id: UUID
    sort_order: int
    public_url: str
    caption: str | None
    alt_text: str | None
    width: int | None
    height: int | None
    mime_type: str


class GalleryAddRequest(BaseModel):
    media_id: UUID


class GalleryReorderRequest(BaseModel):
    media_ids: list[UUID] = Field(min_length=0)


class GalleryReplaceRequest(BaseModel):
    media_ids: list[UUID] = Field(min_length=0)
