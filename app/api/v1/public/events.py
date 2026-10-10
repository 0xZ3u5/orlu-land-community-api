from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.schemas.event import EventResponse
from app.services.events import get_event_by_slug, list_events
from app.services.featured_media_responses import (
    serialize_event,
    serialize_events,
)

router = APIRouter(
    prefix="/events",
    tags=["Public Events"],
)


@router.get(
    "",
    response_model=list[EventResponse],
)
def list_public_events(
    db: Annotated[Session, Depends(get_db)],
) -> list[EventResponse]:
    events = list_events(
        db=db,
        include_unpublished=False,
    )
    return serialize_events(db, events)


@router.get(
    "/{slug}",
    response_model=EventResponse,
)
def get_public_event(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
) -> EventResponse:
    event = get_event_by_slug(
        db=db,
        slug=slug,
        include_unpublished=False,
    )

    if event is None:
        raise ResourceNotFoundError("Event not found.")

    return serialize_event(db, event)
