from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.schemas.community_profile import PublicCommunityProfileResponse
from app.services.community_profiles import (
    get_community_profile,
    list_community_profiles,
    serialize_public_community_profile,
)

router = APIRouter(
    prefix="/community-profiles",
    tags=["Public Community Profiles"],
)


@router.get(
    "",
    response_model=list[PublicCommunityProfileResponse],
)
def list_public_profiles(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return [
        serialize_public_community_profile(item)
        for item in list_community_profiles(db, published_only=True)
    ]


@router.get(
    "/{profile_id}",
    response_model=PublicCommunityProfileResponse,
)
def get_public_profile(
    profile_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    item = get_community_profile(
        db,
        profile_id,
        published_only=True,
    )
    if item is None:
        raise ResourceNotFoundError("Community profile not found.")
    return serialize_public_community_profile(item)
