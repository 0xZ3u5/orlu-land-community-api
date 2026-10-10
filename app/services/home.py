from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event, EventStatus
from app.models.post import Post, PostStatus
from app.models.site_setting import SiteSetting


def get_home_data(db: Session) -> dict:
    now = datetime.now(timezone.utc)

    site_statement = select(SiteSetting).limit(1)
    site = db.scalar(site_statement)

    featured_posts_statement = (
        select(Post)
        .where(
            Post.status == PostStatus.PUBLISHED,
            Post.featured.is_(True),
        )
        .order_by(Post.created_at.desc())
        .limit(3)
    )
    featured_posts = list(db.scalars(featured_posts_statement).all())

    latest_posts_statement = (
        select(Post)
        .where(Post.status == PostStatus.PUBLISHED)
        .order_by(Post.created_at.desc())
    )
    latest_posts = list(db.scalars(latest_posts_statement).all())

    upcoming_events_statement = (
        select(Event)
        .where(
            Event.status == EventStatus.PUBLISHED,
            Event.start_at >= now,
        )
        .order_by(Event.start_at.asc())
    )
    upcoming_events = list(db.scalars(upcoming_events_statement).all())

    return {
        "site": site,
        "featured_posts": featured_posts,
        "latest_posts": latest_posts,
        "upcoming_events": upcoming_events,
    }
