from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.schemas.site import SiteResponse
from app.services.site import get_site_settings

router = APIRouter(
    prefix="/site",
    tags=["Public Site"],
)


@router.get(
    "",
    response_model=SiteResponse,
)
def get_public_site(
    db: Annotated[Session, Depends(get_db)],
) -> SiteResponse:
    site_settings = get_site_settings(db=db)

    if site_settings is None:
        raise ResourceNotFoundError("Site settings not found.")

    return site_settings
