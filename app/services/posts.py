import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import Post, PostStatus
from app.models.author import Author
from app.models.category import Category
from app.models.media import Media


def list_posts(
    db: Session,
    *,
    include_unpublished: bool = False,
) -> list[Post]:
    statement = select(Post).order_by(Post.created_at.desc())

    if not include_unpublished:
        statement = statement.where(Post.status == PostStatus.PUBLISHED)

    return list(db.scalars(statement).all())


def get_post_by_id(
    db: Session,
    post_id: uuid.UUID,
) -> Post | None:
    statement = select(Post).where(Post.id == post_id)
    return db.scalar(statement)


def get_post_by_slug(
    db: Session,
    slug: str,
    *,
    include_unpublished: bool = False,
) -> Post | None:
    statement = select(Post).where(Post.slug == slug)

    if not include_unpublished:
        statement = statement.where(Post.status == PostStatus.PUBLISHED)

    return db.scalar(statement)


def validate_post_status(
    status: PostStatus,
    scheduled_at: datetime | None,
    published_at: datetime | None,
) -> None:
    now = datetime.now(timezone.utc)

    if status == PostStatus.DRAFT:
        if scheduled_at is not None:
            raise ValueError("Draft posts cannot have a scheduled_at value.")

        if published_at is not None:
            raise ValueError("Draft posts cannot have a published_at value.")

    elif status == PostStatus.SCHEDULED:
        if scheduled_at is None:
            raise ValueError(
                "Scheduled posts require a scheduled_at value."
            )

        if scheduled_at <= now:
            raise ValueError(
                "scheduled_at must be in the future."
            )

        if published_at is not None:
            raise ValueError(
                "Scheduled posts cannot have a published_at value."
            )

    elif status == PostStatus.PUBLISHED:
        if published_at is None:
            raise ValueError(
                "Published posts require a published_at value."
            )

        if scheduled_at is not None:
            raise ValueError(
                "Published posts cannot have a scheduled_at value."
            )


def create_post(
    db: Session,
    *,
    title: str,
    slug: str,
    excerpt: str | None,
    content: str,
    status: PostStatus,
    scheduled_at: datetime | None,
    published_at: datetime | None,
    featured: bool,
    featured_media_id: uuid.UUID | None,
    author_id: uuid.UUID,
    category_id: uuid.UUID,
    event_id: uuid.UUID | None,
    video_url: str | None,
) -> Post:
    validate_post_relationships(
    db=db,
    author_id=author_id,
    category_id=category_id,
    featured_media_id=featured_media_id,
    )

    validate_post_status(
        status=status,
        scheduled_at=scheduled_at,
        published_at=published_at,
    )

    post = Post(
        id=uuid.uuid4(),
        title=title,
        slug=slug,
        excerpt=excerpt,
        content=content,
        status=status,
        scheduled_at=scheduled_at,
        published_at=published_at,
        featured=featured,
        featured_media_id=featured_media_id,
        author_id=author_id,
        category_id=category_id,
        event_id=event_id,
        video_url=video_url,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

def update_post(
    db: Session,
    *,
    post: Post,
    title: str | None = None,
    slug: str | None = None,
    excerpt: str | None = None,
    content: str | None = None,
    status: PostStatus | None = None,
    scheduled_at: datetime | None = None,
    published_at: datetime | None = None,
    featured: bool | None = None,
    featured_media_id: uuid.UUID | None = None,
    author_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    event_id: uuid.UUID | None = None,
    video_url: str | None = None,
) -> Post:
    new_status = status if status is not None else post.status
    new_scheduled_at = (
        scheduled_at
        if scheduled_at is not None
        else post.scheduled_at
    )
    new_published_at = (
        published_at
        if published_at is not None
        else post.published_at
    )

    new_author_id = (
        author_id
        if author_id is not None
        else post.author_id
    )
    new_category_id = (
        category_id
        if category_id is not None
        else post.category_id
    )

    new_featured_media_id = (
        featured_media_id
        if featured_media_id is not None
        else post.featured_media_id
    )

    validate_post_relationships(
        db=db,
        author_id=new_author_id,
        category_id=new_category_id,
        featured_media_id=new_featured_media_id,
    )

    validate_post_status(
        status=new_status,
        scheduled_at=new_scheduled_at,
        published_at=new_published_at,
    )

    if title is not None:
        post.title = title

    if slug is not None:
        post.slug = slug

    if excerpt is not None:
        post.excerpt = excerpt

    if content is not None:
        post.content = content

    if status is not None:
        post.status = status

    if scheduled_at is not None:
        post.scheduled_at = scheduled_at

    if published_at is not None:
        post.published_at = published_at

    if featured is not None:
        post.featured = featured

    if featured_media_id is not None:
        post.featured_media_id = featured_media_id

    if author_id is not None:
        post.author_id = author_id

    if category_id is not None:
        post.category_id = category_id

    if event_id is not None:
        post.event_id = event_id

    if video_url is not None:
        post.video_url = video_url

    db.commit()
    db.refresh(post)

    return post

def delete_post(
    db: Session,
    *,
    post: Post,
) -> None:
    db.delete(post)
    db.commit()

def validate_post_relationships(
    db: Session,
    *,
    author_id: uuid.UUID,
    category_id: uuid.UUID,
    featured_media_id: uuid.UUID | None = None,
) -> None:
    author = db.scalar(
        select(Author).where(Author.id == author_id)
    )

    if author is None:
        raise ValueError("Author not found.")

    category = db.scalar(
        select(Category).where(Category.id == category_id)
    )

    if category is None:
        raise ValueError("Category not found.")

    if featured_media_id is not None:
        media = db.scalar(
            select(Media).where(Media.id == featured_media_id)
        )

        if media is None:
            raise ValueError("Featured media not found.")
