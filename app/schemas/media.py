
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field

from app.models.media import MediaType
from app.services.r2_storage import get_public_media_url


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

    @computed_field
    @property
    def public_url(self) -> str:
        return get_public_media_url(self.storage_key)
