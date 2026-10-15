from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.community_profile import (
    CommunityProfileCreate,
    CommunityProfileOrderRequest,
    CommunityProfileResponse,
    CommunityProfileUpdate,
)
from app.services.community_profiles import (
    create_community_profile,
    delete_community_profile,
    get_community_profile,
    list_community_profiles,
    reorder_community_profiles,
    serialize_community_profile,
    update_community_profile,
)

router = APIRouter(
    prefix="/admin/community-profiles",
    tags=["Admin Community Profiles"],
)


@router.post(
    "",
    response_model=CommunityProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile_endpoint(
    payload: CommunityProfileCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> CommunityProfileResponse:
    try:
        item = create_community_profile(
            db,
            name=payload.name,
            category=payload.category,
            biography=payload.biography,
            profile_media_id=payload.profile_media_id,
            is_published=payload.is_published,
            display_order=payload.display_order,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_community_profile(item)


@router.get(
    "",
    response_model=list[CommunityProfileResponse],
)
def list_profiles_endpoint(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    return [
        serialize_community_profile(item)
        for item in list_community_profiles(db)
    ]


# Register the static /order route before /{profile_id}.
@router.patch(
    "/order",
    status_code=status.HTTP_204_NO_CONTENT,
)
def reorder_profiles_endpoint(
    payload: CommunityProfileOrderRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    try:
        reorder_community_profiles(db, profile_ids=payload.profile_ids)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/{profile_id}",
    response_model=CommunityProfileResponse,
)
def get_profile_endpoint(
    profile_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    item = get_community_profile(db, profile_id)
    if item is None:
        raise ResourceNotFoundError("Community profile not found.")
    return serialize_community_profile(item)


@router.patch(
    "/{profile_id}",
    response_model=CommunityProfileResponse,
)
def update_profile_endpoint(
    profile_id: UUID,
    payload: CommunityProfileUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    item = get_community_profile(db, profile_id)
    if item is None:
        raise ResourceNotFoundError("Community profile not found.")

    updates = payload.model_dump(exclude_unset=True)

    for field in ("name", "category"):
        if field in updates and updates[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null.",
            )

    try:
        updated = update_community_profile(db, item[0], updates)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_community_profile(updated)


@router.delete(
    "/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_profile_endpoint(
    profile_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    item = get_community_profile(db, profile_id)
    if item is None:
        raise ResourceNotFoundError("Community profile not found.")
    delete_community_profile(db, item[0])
