from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.page import PageResponse, PageUpdate
from app.services.pages import get_page_by_slug, update_page

router = APIRouter(
    prefix="/admin/pages",
    tags=["Admin Pages"],
)


@router.get(
    "/{slug}",
    response_model=PageResponse,
)
def get_admin_page(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> PageResponse:
    page = get_page_by_slug(
        db=db,
        slug=slug,
    )

    if page is None:
        raise ResourceNotFoundError("Page not found.")

    return page


@router.patch(
    "/{slug}",
    response_model=PageResponse,
)
def update_admin_page(
    slug: str,
    page_data: PageUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> PageResponse:
    page = get_page_by_slug(
        db=db,
        slug=slug,
    )

    if page is None:
        raise ResourceNotFoundError("Page not found.")

    return update_page(
        db=db,
        page=page,
        title=page_data.title,
        content=page_data.content,
    )
