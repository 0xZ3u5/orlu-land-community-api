from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.site import SiteResponse, SiteUpdate
from app.services.site import get_site_settings, update_site_settings

router = APIRouter(
    prefix="/admin/site",
    tags=["Admin Site"],
)


@router.get(
    "",
    response_model=SiteResponse,
)
def get_admin_site(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> SiteResponse:
    site_settings = get_site_settings(db=db)

    if site_settings is None:
        raise ResourceNotFoundError("Site settings not found.")

    return site_settings


@router.patch(
    "",
    response_model=SiteResponse,
)
def update_admin_site(
    site_data: SiteUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> SiteResponse:
    site_settings = get_site_settings(db=db)

    if site_settings is None:
        raise ResourceNotFoundError("Site settings not found.")

    return update_site_settings(
        db=db,
        site_settings=site_settings,
        community_name=site_data.community_name,
        description=site_data.description,
        logo_media_id=site_data.logo_media_id,
        email=site_data.email,
        phone=site_data.phone,
        address=site_data.address,
        whatsapp_url=site_data.whatsapp_url,
    )
