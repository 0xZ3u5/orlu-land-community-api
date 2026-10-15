import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.author import Author
from app.models.community_profile import CommunityProfile
from app.models.event import Event
from app.models.event_media import EventMedia
from app.models.gallery_media import GalleryMedia
from app.models.media import Media, MediaType
from app.models.post import Post
from app.models.post_media import PostMedia
from app.models.site_setting import SiteSetting


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


def is_media_in_use(
    db: Session,
    *,
    media_id: uuid.UUID,
) -> bool:
    references = (
        select(Post.id).where(Post.featured_media_id == media_id),
        select(Event.id).where(Event.featured_media_id == media_id),
        select(Author.id).where(Author.profile_media_id == media_id),
        select(CommunityProfile.id).where(
            CommunityProfile.profile_media_id == media_id
        ),
        select(SiteSetting.id).where(SiteSetting.logo_media_id == media_id),
        select(PostMedia.post_id).where(PostMedia.media_id == media_id),
        select(EventMedia.event_id).where(EventMedia.media_id == media_id),
        select(GalleryMedia.media_id).where(GalleryMedia.media_id == media_id),
    )
    statement = select(or_(*(query.exists() for query in references)))
    return bool(db.scalar(statement))
