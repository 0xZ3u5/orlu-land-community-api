from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.category import CategoryResponse
from app.services.categories import get_category_by_slug, list_categories
from app.core.errors import ResourceNotFoundError

router = APIRouter(prefix="/categories", tags=["Public Categories"])


@router.get("", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
) -> list[CategoryResponse]:
    return list_categories(db)


@router.get("/{slug}", response_model=CategoryResponse)
def get_category(
    slug: str,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    category = get_category_by_slug(db, slug)

    if category is None:
        raise ResourceNotFoundError("Category not found.")
    return category
