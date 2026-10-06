from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.media import MediaType


class MediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    media_type: MediaType
    storage_key: str
    original_filename: str
    mime_type: str
    file_size: int
    width: int | None
    height: int | None
    caption: str | None
    alt_text: str | None
    created_at: datetime
    updated_at: datetime
