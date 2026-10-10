import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event, EventStatus
from app.models.media import Media


def validate_event_media(
    db: Session,
    featured_media_id: uuid.UUID | None,
) -> None:
    if featured_media_id is None:
        return

    media = db.scalar(
        select(Media).where(Media.id == featured_media_id)
    )

    if media is None:
        raise ValueError("Featured media not found.")


def list_events(
    db: Session,
    *,
    include_unpublished: bool = False,
) -> list[Event]:
    statement = select(Event).order_by(Event.start_at.asc())

    if not include_unpublished:
        statement = statement.where(
            Event.status == EventStatus.PUBLISHED
        )

    return list(db.scalars(statement).all())


def get_event_by_id(
    db: Session,
    event_id: uuid.UUID,
) -> Event | None:
    statement = select(Event).where(Event.id == event_id)
    return db.scalar(statement)


def get_event_by_slug(
    db: Session,
    slug: str,
    *,
    include_unpublished: bool = False,
) -> Event | None:
    statement = select(Event).where(Event.slug == slug)

    if not include_unpublished:
        statement = statement.where(
            Event.status == EventStatus.PUBLISHED
        )

    return db.scalar(statement)


def validate_event_status(
    status: EventStatus,
    start_at: datetime,
    end_at: datetime | None,
) -> None:
    if end_at is not None and end_at < start_at:
        raise ValueError(
            "end_at cannot be earlier than start_at."
        )

    if status == EventStatus.PUBLISHED:
        if start_at is None:
            raise ValueError(
                "Published events require a start_at value."
            )


def create_event(
    db: Session,
    *,
    title: str,
    slug: str,
    description: str,
    start_at: datetime,
    end_at: datetime | None,
    location: str | None,
    status: EventStatus,
    featured_media_id: uuid.UUID | None,
) -> Event:
    validate_event_status(
        status=status,
        start_at=start_at,
        end_at=end_at,
    )

    validate_event_media(
        db=db,
        featured_media_id=featured_media_id,
    )

    event = Event(
        id=uuid.uuid4(),
        title=title,
        slug=slug,
        description=description,
        start_at=start_at,
        end_at=end_at,
        location=location,
        status=status,
        featured_media_id=featured_media_id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event

def update_event(
    db: Session,
    *,
    event: Event,
    title: str | None = None,
    slug: str | None = None,
    description: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    location: str | None = None,
    status: EventStatus | None = None,
    featured_media_id: uuid.UUID | None = None,
    featured_media_id_provided: bool = False,
) -> Event:
    new_start_at = (
        start_at
        if start_at is not None
        else event.start_at
    )

    new_end_at = (
        end_at
        if end_at is not None
        else event.end_at
    )

    new_status = (
        status
        if status is not None
        else event.status
    )

    new_featured_media_id = (
        featured_media_id
        if featured_media_id_provided
        else event.featured_media_id
    )

    validate_event_media(
        db=db,
        featured_media_id=new_featured_media_id,
    )

    validate_event_status(
        status=new_status,
        start_at=new_start_at,
        end_at=new_end_at,
    )

    if title is not None:
        event.title = title

    if slug is not None:
        event.slug = slug

    if description is not None:
        event.description = description

    if start_at is not None:
        event.start_at = start_at

    if end_at is not None:
        event.end_at = end_at

    if location is not None:
        event.location = location

    if status is not None:
        event.status = status

    if featured_media_id_provided:
        event.featured_media_id = featured_media_id

    db.commit()
    db.refresh(event)

    return event


def delete_event(
    db: Session,
    *,
    event: Event,
) -> None:
    db.delete(event)
    db.commit()
