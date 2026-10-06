import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.media import MediaResponse
from app.services.media import delete_media, get_media_by_id, list_media

router = APIRouter(
    prefix="/admin/media",
    tags=["Admin Media"],
)


@router.get(
    "",
    response_model=list[MediaResponse],
)
def list_admin_media(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[MediaResponse]:
    return list_media(db=db)


@router.get(
    "/{media_id}",
    response_model=MediaResponse,
)
def get_admin_media(
    media_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> MediaResponse:
    media = get_media_by_id(
        db=db,
        media_id=media_id,
    )

    if media is None:
        raise ResourceNotFoundError("Media not found.")

    return media


@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_admin_media(
    media_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> Response:
    media = get_media_by_id(
        db=db,
        media_id=media_id,
    )

    if media is None:
        raise ResourceNotFoundError("Media not found.")

    delete_media(
        db=db,
        media=media,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
