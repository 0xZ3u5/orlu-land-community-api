import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.media import Media, MediaType


def list_media(db: Session) -> list[Media]:
    statement = select(Media).order_by(Media.created_at.desc())
    return list(db.scalars(statement).all())


def get_media_by_id(
    db: Session,
    media_id: uuid.UUID,
) -> Media | None:
    statement = select(Media).where(Media.id == media_id)
    return db.scalar(statement)


def create_media(
    db: Session,
    *,
    media_type: MediaType,
    storage_key: str,
    original_filename: str,
    mime_type: str,
    file_size: int,
    width: int | None = None,
    height: int | None = None,
    caption: str | None = None,
    alt_text: str | None = None,
) -> Media:
    media = Media(
        media_type=media_type,
        storage_key=storage_key,
        original_filename=original_filename,
        mime_type=mime_type,
        file_size=file_size,
        width=width,
        height=height,
        caption=caption,
        alt_text=alt_text,
    )

    db.add(media)
    db.commit()
    db.refresh(media)

    return media


def delete_media(
    db: Session,
    *,
    media: Media,
) -> None:
    db.delete(media)
    db.commit()
