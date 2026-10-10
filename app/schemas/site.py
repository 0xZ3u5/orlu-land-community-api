from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class SiteUpdate(BaseModel):
    community_name: str
    description: str | None = None
    logo_media_id: UUID | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    whatsapp_url: str | None = None


class SiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    community_name: str
    description: str | None
    logo_media_id: UUID | None
    email: EmailStr | None
    phone: str | None
    address: str | None
    whatsapp_url: str | None
    created_at: datetime
    updated_at: datetime
