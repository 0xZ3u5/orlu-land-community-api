from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.schemas.post import PostResponse
from app.services.posts import get_post_by_slug, list_posts
from app.services.featured_media_responses import (
    serialize_post,
    serialize_posts,
)

router = APIRouter(
    prefix="/posts",
    tags=["Public Posts"],
)


@router.get("", response_model=list[PostResponse])
def list_public_posts(
    db: Annotated[Session, Depends(get_db)],
) -> list[PostResponse]:
    posts = list_posts(
        db=db,
        include_unpublished=False,
    )
    return serialize_posts(db, posts)


@router.get("/{slug}", response_model=PostResponse)
def get_public_post(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
) -> PostResponse:
    post = get_post_by_slug(
        db=db,
        slug=slug,
        include_unpublished=False,
    )

    if post is None:
        raise ResourceNotFoundError("Post not found.")

    return serialize_post(db, post)
