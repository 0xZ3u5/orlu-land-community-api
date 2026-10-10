from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.featured_media_responses import (
    serialize_event,
    serialize_events,
)
from app.services.events import (
    create_event,
    delete_event,
    get_event_by_id,
    list_events,
    update_event,
)

router = APIRouter(
    prefix="/admin/events",
    tags=["Admin Events"],
)


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event_endpoint(
    event_data: EventCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventResponse:
    try:
        event = create_event(
            db=db,
            title=event_data.title,
            slug=event_data.slug,
            description=event_data.description,
            start_at=event_data.start_at,
            end_at=event_data.end_at,
            location=event_data.location,
            status=event_data.status,
            featured_media_id=event_data.featured_media_id,
        )
        return serialize_event(db, event)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[EventResponse],
)
def list_admin_events_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[EventResponse]:
    events = list_events(
        db=db,
        include_unpublished=True,
    )
    return serialize_events(db, events)


@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def get_admin_event_endpoint(
    event_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventResponse:
    event = get_event_by_id(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise ResourceNotFoundError("Event not found.")

    return serialize_event(db, event)

@router.patch(
    "/{event_id}",
    response_model=EventResponse,
)
def update_admin_event_endpoint(
    event_id: UUID,
    event_data: EventUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventResponse:
    event = get_event_by_id(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise ResourceNotFoundError("Event not found.")

    try:
        updated_event = update_event(
            db=db,
            event=event,
            title=event_data.title,
            slug=event_data.slug,
            description=event_data.description,
            start_at=event_data.start_at,
            end_at=event_data.end_at,
            location=event_data.location,
            status=event_data.status,
            featured_media_id=event_data.featured_media_id,
            featured_media_id_provided=(
                "featured_media_id" in event_data.model_fields_set
            ),
        )
        return serialize_event(db, updated_event)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_admin_event_endpoint(
    event_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    event = get_event_by_id(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise ResourceNotFoundError("Event not found.")

    delete_event(
        db=db,
        event=event,
    )
