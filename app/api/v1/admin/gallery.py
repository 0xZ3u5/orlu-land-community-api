from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.gallery import (
    GalleryAddRequest,
    GalleryImageResponse,
    GalleryReplaceRequest,
    GalleryReorderRequest,
)
from app.services.gallery import (
    add_to_standalone_gallery,
    list_event_gallery,
    list_post_gallery,
    list_standalone_gallery,
    remove_from_standalone_gallery,
    reorder_standalone_gallery,
    replace_event_gallery,
    replace_post_gallery,
)
from app.services.gallery_responses import serialize_gallery_items
from app.services.events import get_event_by_id
from app.services.media import get_media_by_id
from app.services.posts import get_post_by_id

router = APIRouter(prefix="/admin", tags=["Admin Gallery"])


@router.get("/gallery", response_model=list[GalleryImageResponse])
def get_admin_gallery(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[GalleryImageResponse]:
    return serialize_gallery_items(list_standalone_gallery(db))


@router.post(
    "/gallery",
    response_model=GalleryImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_admin_gallery_item(
    payload: GalleryAddRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> GalleryImageResponse:
    try:
        item = add_to_standalone_gallery(db, media_id=payload.media_id)
    except ValueError as exc:
        code = (
            status.HTTP_409_CONFLICT
            if "already" in str(exc).lower()
            else status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(status_code=code, detail=str(exc)) from exc

    media = get_media_by_id(db, item.media_id)
    if media is None:
        raise ResourceNotFoundError("Media not found.")
    return serialize_gallery_items([(media, item.sort_order)])[0]


@router.patch("/gallery/order", status_code=status.HTTP_204_NO_CONTENT)
def reorder_admin_gallery(
    payload: GalleryReorderRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    try:
        reorder_standalone_gallery(db, media_ids=payload.media_ids)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.delete(
    "/gallery/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_admin_gallery_item(
    media_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    try:
        remove_from_standalone_gallery(db, media_id=media_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/posts/{post_id}/media",
    response_model=list[GalleryImageResponse],
)
def get_admin_post_gallery(
    post_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[GalleryImageResponse]:
    try:
        items = list_post_gallery(db, post_id=post_id)
    except ValueError as exc:
        raise ResourceNotFoundError(str(exc)) from exc
    return serialize_gallery_items(items)


@router.put(
    "/posts/{post_id}/media",
    response_model=list[GalleryImageResponse],
)
def replace_admin_post_gallery(
    post_id: UUID,
    payload: GalleryReplaceRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[GalleryImageResponse]:
    try:
        replace_post_gallery(db, post_id=post_id, media_ids=payload.media_ids)
        return serialize_gallery_items(list_post_gallery(db, post_id=post_id))
    except ValueError as exc:
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc).lower()
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Post gallery could not be updated.",
        ) from exc


@router.get(
    "/events/{event_id}/media",
    response_model=list[GalleryImageResponse],
)
def get_admin_event_gallery(
    event_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[GalleryImageResponse]:
    try:
        items = list_event_gallery(db, event_id=event_id)
    except ValueError as exc:
        raise ResourceNotFoundError(str(exc)) from exc
    return serialize_gallery_items(items)


@router.put(
    "/events/{event_id}/media",
    response_model=list[GalleryImageResponse],
)
def replace_admin_event_gallery(
    event_id: UUID,
    payload: GalleryReplaceRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[GalleryImageResponse]:
    try:
        replace_event_gallery(db, event_id=event_id, media_ids=payload.media_ids)
        return serialize_gallery_items(list_event_gallery(db, event_id=event_id))
    except ValueError as exc:
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc).lower()
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Event gallery could not be updated.",
        ) from exc
