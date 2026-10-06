from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.author import (
    AuthorCreate,
    AuthorResponse,
    AuthorUpdate,
)
from app.services.authors import (
    create_author,
    delete_author,
    get_author_by_id,
    list_authors,
    update_author,
)

router = APIRouter(
    prefix="/admin/authors",
    tags=["Admin Authors"],
)


@router.post(
    "",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_author_endpoint(
    author_data: AuthorCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorResponse:
    return create_author(
        db=db,
        name=author_data.name,
        biography=author_data.biography,
        profile_media_id=author_data.profile_media_id,
    )


@router.get(
    "",
    response_model=list[AuthorResponse],
)
def list_authors_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[AuthorResponse]:
    return list_authors(db)


@router.get(
    "/{author_id}",
    response_model=AuthorResponse,
)
def get_author_endpoint(
    author_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorResponse:
    author = get_author_by_id(
        db=db,
        author_id=author_id,
    )

    if author is None:
        raise ResourceNotFoundError("Author not found.")

    return author

@router.patch(
    "/{author_id}",
    response_model=AuthorResponse,
)
def update_author_endpoint(
    author_id: UUID,
    author_data: AuthorUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorResponse:
    author = get_author_by_id(
        db=db,
        author_id=author_id,
    )

    if author is None:
        raise ResourceNotFoundError("Author not found.")

    return update_author(
        db=db,
        author=author,
        name=author_data.name,
        biography=author_data.biography,
        profile_media_id=author_data.profile_media_id,
    )

@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_author_endpoint(
    author_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    author = get_author_by_id(
        db=db,
        author_id=author_id,
    )

    if author is None:
        raise ResourceNotFoundError("Author not found.")

    delete_author(
        db=db,
        author=author,
    )
