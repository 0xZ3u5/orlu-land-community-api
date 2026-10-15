from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: DocumentStatus | None = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    original_filename: str
    mime_type: str
    file_size: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


class PublicDocumentResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    file_size: int
    created_at: datetime
    download_url: str
