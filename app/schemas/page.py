from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PageUpdate(BaseModel):
    title: str
    content: str


class PageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
