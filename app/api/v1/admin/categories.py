from uuid import UUID

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.errors import ResourceNotFoundError
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import (
        CategoryCreate, 
        CategoryResponse,
        CategoryUpdate,
    )
from app.services.categories import (
        create_category, 
        list_admin_categories, 
        get_category_by_id,
        update_category,
        delete_category,

    )

router = APIRouter(
    prefix="/admin/categories",
    tags=["Admin Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category_endpoint(
    category_data: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CategoryResponse:
    return create_category(
        db=db,
        name=category_data.name,
        slug=category_data.slug,
        description=category_data.description,
    )

@router.get(
    "",
    response_model=list[CategoryResponse],
)
def list_admin_categories_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[CategoryResponse]:
    return list_admin_categories(db)

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_admin_category(
    category_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CategoryResponse:
    category = get_category_by_id(db, category_id)

    if category is None:
        raise ResourceNotFoundError("Category not found.")

    return category

@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category_endpoint(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CategoryResponse:
    category = get_category_by_id(db, category_id)

    if category is None:
        raise ResourceNotFoundError("Category not found.")

    return update_category(
        db=db,
        category=category,
        name=category_data.name,
        slug=category_data.slug,
        description=category_data.description,
    )

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category_endpoint(
    category_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    category = get_category_by_id(db, category_id)

    if category is None:
        raise ResourceNotFoundError("Category not found.")

    delete_category(
        db=db,
        category=category,
    )
