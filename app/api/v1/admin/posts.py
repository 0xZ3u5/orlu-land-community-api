from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services.posts import (
    create_post,
    get_post_by_id,
    list_posts,
    update_post,
    delete_post,
)

router = APIRouter(
    prefix="/admin/posts",
    tags=["Admin Posts"],
)


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post_endpoint(
    post_data: PostCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PostResponse:
    try:
        return create_post(
            db=db,
            title=post_data.title,
            slug=post_data.slug,
            excerpt=post_data.excerpt,
            content=post_data.content,
            status=post_data.status,
            scheduled_at=post_data.scheduled_at,
            published_at=post_data.published_at,
            featured=post_data.featured,
            featured_media_id=post_data.featured_media_id,
            author_id=post_data.author_id,
            category_id=post_data.category_id,
            event_id=post_data.event_id,
            video_url=(
                str(post_data.video_url)
                if post_data.video_url is not None
                else None
            ),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[PostResponse],
)
def list_admin_posts_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[PostResponse]:
    return list_posts(
        db=db,
        include_unpublished=True,
    )


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
def get_admin_post_endpoint(
    post_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PostResponse:
    post = get_post_by_id(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise ResourceNotFoundError("Post not found.")

    return post


@router.patch(
    "/{post_id}",
    response_model=PostResponse,
)
def update_admin_post_endpoint(
    post_id: UUID,
    post_data: PostUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PostResponse:
    post = get_post_by_id(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise ResourceNotFoundError("Post not found.")

    try:
        return update_post(
        db=db,
        post=post,
        title=post_data.title,
        slug=post_data.slug,
        excerpt=post_data.excerpt,
        content=post_data.content,
        status=post_data.status,
        scheduled_at=post_data.scheduled_at,
        published_at=post_data.published_at,
        featured=post_data.featured,
        featured_media_id=post_data.featured_media_id,
        author_id=post_data.author_id,
        category_id=post_data.category_id,
        event_id=post_data.event_id,
        video_url=(
            str(post_data.video_url)
            if post_data.video_url is not None
            else None
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_admin_post_endpoint(
    post_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    post = get_post_by_id(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise ResourceNotFoundError("Post not found.")

    delete_post(
        db=db,
        post=post,
    )
