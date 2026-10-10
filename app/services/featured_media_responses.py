from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.event_media import EventMedia
from app.models.media import Media
from app.models.post import Post
from app.models.post_media import PostMedia
from app.schemas.event import EventResponse
from app.schemas.gallery import GalleryImageResponse
from app.schemas.post import PostResponse
from app.services.r2_storage import get_public_media_url


def featured_media_url_map(
    db: Session,
    *,
    posts: Sequence[Post] = (),
    events: Sequence[Event] = (),
) -> dict[UUID, str]:
    media_ids = {
        item.featured_media_id
        for item in (*posts, *events)
        if item.featured_media_id is not None
    }

    if not media_ids:
        return {}

    media_items = db.scalars(
        select(Media).where(Media.id.in_(media_ids))
    ).all()

    return {
        media.id: get_public_media_url(media.storage_key)
        for media in media_items
    }


def gallery_images_map(
    db: Session,
    *,
    posts: Sequence[Post] = (),
    events: Sequence[Event] = (),
) -> dict[UUID, list[GalleryImageResponse]]:
    """Bulk-load gallery images for a batch of posts and events."""
    result: dict[UUID, list[GalleryImageResponse]] = {}
    post_ids = {post.id for post in posts}
    event_ids = {event.id for event in events}

    if post_ids:
        rows = db.execute(
            select(PostMedia.post_id, PostMedia.sort_order, Media)
            .join(Media, Media.id == PostMedia.media_id)
            .where(PostMedia.post_id.in_(post_ids))
            .order_by(
                PostMedia.post_id,
                PostMedia.sort_order,
                Media.created_at,
            )
        ).all()

        for post_id, sort_order, media in rows:
            result.setdefault(post_id, []).append(
                GalleryImageResponse(
                    media_id=media.id,
                    sort_order=sort_order,
                    public_url=get_public_media_url(media.storage_key),
                    caption=media.caption,
                    alt_text=media.alt_text,
                    width=media.width,
                    height=media.height,
                    mime_type=media.mime_type,
                )
            )

    if event_ids:
        rows = db.execute(
            select(EventMedia.event_id, EventMedia.sort_order, Media)
            .join(Media, Media.id == EventMedia.media_id)
            .where(EventMedia.event_id.in_(event_ids))
            .order_by(
                EventMedia.event_id,
                EventMedia.sort_order,
                Media.created_at,
            )
        ).all()

        for event_id, sort_order, media in rows:
            result.setdefault(event_id, []).append(
                GalleryImageResponse(
                    media_id=media.id,
                    sort_order=sort_order,
                    public_url=get_public_media_url(media.storage_key),
                    caption=media.caption,
                    alt_text=media.alt_text,
                    width=media.width,
                    height=media.height,
                    mime_type=media.mime_type,
                )
            )

    return result


def serialize_post(
    db: Session,
    post: Post,
) -> PostResponse:
    urls = featured_media_url_map(db, posts=(post,))
    galleries = gallery_images_map(db, posts=(post,))
    return PostResponse.model_validate(post).model_copy(
        update={
            "featured_media_url": urls.get(post.featured_media_id),
            "gallery_images": galleries.get(post.id, []),
        }
    )

def serialize_posts(
    db: Session,
    posts: Sequence[Post],
) -> list[PostResponse]:
    urls = featured_media_url_map(db, posts=posts)
    galleries = gallery_images_map(db, posts=posts)
    return [
        PostResponse.model_validate(post).model_copy(
            update={
                "featured_media_url": urls.get(post.featured_media_id),
                "gallery_images": galleries.get(post.id, []),
            }
        )
        for post in posts
    ]

def serialize_event(
    db: Session,
    event: Event,
) -> EventResponse:
    urls = featured_media_url_map(db, events=(event,))
    galleries = gallery_images_map(db, events=(event,))
    return EventResponse.model_validate(event).model_copy(
        update={
            "featured_media_url": urls.get(event.featured_media_id),
            "gallery_images": galleries.get(event.id, []),
        }
    )

def serialize_events(
    db: Session,
    events: Sequence[Event],
) -> list[EventResponse]:
    urls = featured_media_url_map(db, events=events)
    galleries = gallery_images_map(db, events=events)
    return [
        EventResponse.model_validate(event).model_copy(
            update={
                "featured_media_url": urls.get(event.featured_media_id),
                "gallery_images": galleries.get(event.id, []),
            }
        )
        for event in events
    ]

def serialize_home_data(
    db: Session,
    home_data: dict,
) -> dict:
    featured_posts = home_data["featured_posts"]
    latest_posts = home_data["latest_posts"]
    upcoming_events = home_data["upcoming_events"]

    all_posts = tuple(featured_posts) + tuple(latest_posts)
    urls = featured_media_url_map(
        db,
        posts=all_posts,
        events=upcoming_events,
    )
    galleries = gallery_images_map(
        db,
        posts=all_posts,
        events=upcoming_events,
    )

    def post_response(post: Post) -> PostResponse:
        return PostResponse.model_validate(post).model_copy(
            update={
                "featured_media_url": urls.get(post.featured_media_id),
                "gallery_images": galleries.get(post.id, []),
            }
        )

    return {
        **home_data,
        "featured_posts": [post_response(post) for post in featured_posts],
        "latest_posts": [post_response(post) for post in latest_posts],
        "upcoming_events": [
            EventResponse.model_validate(event).model_copy(
                update={
                    "featured_media_url": urls.get(event.featured_media_id),
                    "gallery_images": galleries.get(event.id, []),
                }
            )
            for event in upcoming_events
        ],
    }

