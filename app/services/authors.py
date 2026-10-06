import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.author import Author


def list_authors(db: Session) -> list[Author]:
    statement = select(Author).order_by(Author.name.asc())
    return list(db.scalars(statement).all())


def get_author_by_id(
    db: Session,
    author_id: uuid.UUID,
) -> Author | None:
    statement = select(Author).where(Author.id == author_id)
    return db.scalar(statement)


def create_author(
    db: Session,
    name: str,
    biography: str | None = None,
    profile_media_id: uuid.UUID | None = None,
) -> Author:
    author = Author(
        id=uuid.uuid4(),
        name=name,
        biography=biography,
        profile_media_id=profile_media_id,
    )

    db.add(author)
    db.commit()
    db.refresh(author)

    return author

def update_author(
    db: Session,
    author: Author,
    name: str | None = None,
    biography: str | None = None,
    profile_media_id: uuid.UUID | None = None,
) -> Author:
    if name is not None:
        author.name = name

    if biography is not None:
        author.biography = biography

    if profile_media_id is not None:
        author.profile_media_id = profile_media_id

    db.commit()
    db.refresh(author)

    return author

def delete_author(
    db: Session,
    author: Author,
) -> None:
    db.delete(author)
    db.commit()
