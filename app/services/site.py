from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.site_setting import SiteSetting


def get_site_settings(
    db: Session,
) -> SiteSetting | None:
    statement = select(SiteSetting).limit(1)
    return db.scalar(statement)


def update_site_settings(
    db: Session,
    *,
    site_settings: SiteSetting,
    community_name: str,
    description: str | None,
    logo_media_id,
    email: str | None,
    phone: str | None,
    address: str | None,
    whatsapp_url: str | None,
) -> SiteSetting:
    site_settings.community_name = community_name
    site_settings.description = description
    site_settings.logo_media_id = logo_media_id
    site_settings.email = email
    site_settings.phone = phone
    site_settings.address = address
    site_settings.whatsapp_url = whatsapp_url

    db.commit()
    db.refresh(site_settings)

    return site_settings
