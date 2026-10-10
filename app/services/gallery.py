import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.event_media import EventMedia
from app.models.gallery_media import GalleryMedia
from app.models.media import Media
from app.models.post import Post
from app.models.post_media import PostMedia


def _validate_unique_media_ids(media_ids: list[uuid.UUID]) -> None:
    if len(media_ids) != len(set(media_ids)):
        raise ValueError("Duplicate media IDs are not allowed.")


def _validate_media_ids(
    db: Session,
    media_ids: list[uuid.UUID],
) -> None:
    if not media_ids:
        return

    found_ids = set(
        db.scalars(
            select(Media.id).where(Media.id.in_(media_ids))
        ).all()
    )
    missing_ids = set(media_ids) - found_ids

    if missing_ids:
        raise ValueError("One or more media items were not found.")


def list_standalone_gallery(
    db: Session,
) -> list[tuple[Media, int]]:
    statement = (
        select(Media, GalleryMedia.sort_order)
        .join(GalleryMedia, GalleryMedia.media_id == Media.id)
        .order_by(GalleryMedia.sort_order.asc(), Media.created_at.asc())
    )
    return [(media, order) for media, order in db.execute(statement).all()]


def add_to_standalone_gallery(
    db: Session,
    *,
    media_id: uuid.UUID,
) -> GalleryMedia:
    media = db.scalar(select(Media).where(Media.id == media_id))
    if media is None:
        raise ValueError("Media item not found.")

    existing = db.get(GalleryMedia, media_id)
    if existing is not None:
        raise ValueError("Media item is already in the gallery.")

    current_max = db.scalar(select(func.max(GalleryMedia.sort_order)))
    item = GalleryMedia(
        media_id=media_id,
        sort_order=(current_max + 1) if current_max is not None else 0,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def reorder_standalone_gallery(
    db: Session,
    *,
    media_ids: list[uuid.UUID],
) -> None:
    _validate_unique_media_ids(media_ids)

    current_ids = set(
        db.scalars(select(GalleryMedia.media_id)).all()
    )
    requested_ids = set(media_ids)

    if requested_ids != current_ids:
        raise ValueError(
            "Reorder must include every current gallery item exactly once."
        )

    for order, media_id in enumerate(media_ids):
        item = db.get(GalleryMedia, media_id)
        if item is not None:
            item.sort_order = order

    db.commit()


def remove_from_standalone_gallery(
    db: Session,
    *,
    media_id: uuid.UUID,
) -> None:
    item = db.get(GalleryMedia, media_id)
    if item is None:
        raise ValueError("Media item is not in the gallery.")

    db.delete(item)
    db.commit()


def list_post_gallery(
    db: Session,
    *,
    post_id: uuid.UUID,
) -> list[tuple[Media, int]]:
    if db.get(Post, post_id) is None:
        raise ValueError("Post not found.")

    statement = (
        select(Media, PostMedia.sort_order)
        .join(PostMedia, PostMedia.media_id == Media.id)
        .where(PostMedia.post_id == post_id)
        .order_by(PostMedia.sort_order.asc(), Media.created_at.asc())
    )
    return [(media, order) for media, order in db.execute(statement).all()]


def replace_post_gallery(
    db: Session,
    *,
    post_id: uuid.UUID,
    media_ids: list[uuid.UUID],
) -> None:
    if db.get(Post, post_id) is None:
        raise ValueError("Post not found.")

    _validate_unique_media_ids(media_ids)
    _validate_media_ids(db, media_ids)

    db.execute(delete(PostMedia).where(PostMedia.post_id == post_id))
    db.add_all([
        PostMedia(post_id=post_id, media_id=media_id, sort_order=order)
        for order, media_id in enumerate(media_ids)
    ])
    db.commit()


def list_event_gallery(
    db: Session,
    *,
    event_id: uuid.UUID,
) -> list[tuple[Media, int]]:
    if db.get(Event, event_id) is None:
        raise ValueError("Event not found.")

    statement = (
        select(Media, EventMedia.sort_order)
        .join(EventMedia, EventMedia.media_id == Media.id)
        .where(EventMedia.event_id == event_id)
        .order_by(EventMedia.sort_order.asc(), Media.created_at.asc())
    )
    return [(media, order) for media, order in db.execute(statement).all()]


def replace_event_gallery(
    db: Session,
    *,
    event_id: uuid.UUID,
    media_ids: list[uuid.UUID],
) -> None:
    if db.get(Event, event_id) is None:
        raise ValueError("Event not found.")

    _validate_unique_media_ids(media_ids)
    _validate_media_ids(db, media_ids)

    db.execute(delete(EventMedia).where(EventMedia.event_id == event_id))
    db.add_all([
        EventMedia(event_id=event_id, media_id=media_id, sort_order=order)
        for order, media_id in enumerate(media_ids)
    ])
    db.commit()
