import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.community_profile import CommunityProfile
from app.models.media import Media
from app.services.r2_storage import get_public_media_url


def _profile_media_exists(
    db: Session,
    media_id: uuid.UUID,
) -> bool:
    return db.scalar(
        select(Media.id).where(Media.id == media_id)
    ) is not None


def _profile_with_media(
    db: Session,
    profile_id: uuid.UUID,
) -> tuple[CommunityProfile, Media | None] | None:
    statement = (
        select(CommunityProfile, Media)
        .outerjoin(
            Media,
            CommunityProfile.profile_media_id == Media.id,
        )
        .where(CommunityProfile.id == profile_id)
    )
    result = db.execute(statement).first()
    return (result[0], result[1]) if result else None


def list_community_profiles(
    db: Session,
    *,
    published_only: bool = False,
) -> list[tuple[CommunityProfile, Media | None]]:
    statement = (
        select(CommunityProfile, Media)
        .outerjoin(
            Media,
            CommunityProfile.profile_media_id == Media.id,
        )
    )

    if published_only:
        statement = statement.where(CommunityProfile.is_published.is_(True))

    statement = statement.order_by(
        CommunityProfile.display_order.asc(),
        CommunityProfile.name.asc(),
    )
    return list(db.execute(statement).all())


def get_community_profile(
    db: Session,
    profile_id: uuid.UUID,
    *,
    published_only: bool = False,
) -> tuple[CommunityProfile, Media | None] | None:
    result = _profile_with_media(db, profile_id)

    if result is None:
        return None

    profile, media = result
    if published_only and not profile.is_published:
        return None

    return profile, media


def create_community_profile(
    db: Session,
    *,
    name: str,
    category: str,
    biography: str | None = None,
    profile_media_id: uuid.UUID | None = None,
    is_published: bool = False,
    display_order: int = 0,
) -> tuple[CommunityProfile, Media | None]:
    if profile_media_id is not None and not _profile_media_exists(
        db, profile_media_id
    ):
        raise ValueError("Profile photo media item not found.")

    profile = CommunityProfile(
        id=uuid.uuid4(),
        name=name,
        category=category,
        biography=biography,
        profile_media_id=profile_media_id,
        is_published=is_published,
        display_order=display_order,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    result = _profile_with_media(db, profile.id)
    if result is None:
        raise RuntimeError("Created community profile could not be retrieved.")
    return result


def update_community_profile(
    db: Session,
    profile: CommunityProfile,
    updates: dict,
) -> tuple[CommunityProfile, Media | None]:
    if (
        "profile_media_id" in updates
        and updates["profile_media_id"] is not None
        and not _profile_media_exists(db, updates["profile_media_id"])
    ):
        raise ValueError("Profile photo media item not found.")

    allowed_fields = {
        "name",
        "category",
        "biography",
        "profile_media_id",
        "is_published",
        "display_order",
    }
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    result = _profile_with_media(db, profile.id)
    if result is None:
        raise RuntimeError("Updated community profile could not be retrieved.")
    return result


def delete_community_profile(
    db: Session,
    profile: CommunityProfile,
) -> None:
    db.delete(profile)
    db.commit()


def reorder_community_profiles(
    db: Session,
    *,
    profile_ids: list[uuid.UUID],
) -> None:
    if len(profile_ids) != len(set(profile_ids)):
        raise ValueError("Duplicate profile IDs are not allowed.")

    current_ids = set(
        db.scalars(select(CommunityProfile.id)).all()
    )
    if set(profile_ids) != current_ids:
        raise ValueError(
            "Reorder must include every current profile exactly once."
        )

    profiles = {
        profile.id: profile
        for profile in db.scalars(
            select(CommunityProfile).where(
                CommunityProfile.id.in_(profile_ids)
            )
        ).all()
    }

    for order, profile_id in enumerate(profile_ids):
        profiles[profile_id].display_order = order

    db.commit()


def serialize_community_profile(
    item: tuple[CommunityProfile, Media | None],
) -> dict:
    profile, media = item
    return {
        "id": profile.id,
        "name": profile.name,
        "category": profile.category,
        "biography": profile.biography,
        "profile_media_id": profile.profile_media_id,
        "profile_media_url": (
            get_public_media_url(media.storage_key)
            if media is not None
            else None
        ),
        "is_published": profile.is_published,
        "display_order": profile.display_order,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


def serialize_public_community_profile(
    item: tuple[CommunityProfile, Media | None],
) -> dict:
    profile, media = item
    return {
        "id": profile.id,
        "name": profile.name,
        "category": profile.category,
        "biography": profile.biography,
        "profile_media_id": profile.profile_media_id,
        "profile_media_url": (
            get_public_media_url(media.storage_key)
            if media is not None
            else None
        ),
    }
