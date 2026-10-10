from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.schemas.page import PageResponse
from app.services.pages import get_page_by_slug

router = APIRouter(
    prefix="/pages",
    tags=["Public Pages"],
)


@router.get(
    "/{slug}",
    response_model=PageResponse,
)
def get_public_page(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
) -> PageResponse:
    page = get_page_by_slug(
        db=db,
        slug=slug,
    )

    if page is None:
        raise ResourceNotFoundError("Page not found.")

    return page
