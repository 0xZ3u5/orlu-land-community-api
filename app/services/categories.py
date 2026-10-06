import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.core.errors import ResourceNotFoundError


def create_category(
    db: Session,
    name: str,
    slug: str,
    description: str | None = None,
) -> Category:
    category = Category(
        id=uuid.uuid4(),
        name=name,
        slug=slug,
        description=description,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category

def update_category(
    db: Session,
    category: Category,
    name: str | None = None,
    slug: str | None = None,
    description: str | None = None,
) -> Category:
    if name is not None:
        category.name = name

    if slug is not None:
        category.slug = slug

    if description is not None:
        category.description = description

    db.commit()
    db.refresh(category)

    return category

def delete_category(
    db: Session,
    category: Category,
) -> None:
    db.delete(category)
    db.commit()

def list_categories(db: Session) -> list[Category]:
    statement = select(Category).order_by(Category.name.asc())
    return list(db.scalars(statement).all())


def get_category_by_slug(
    db: Session,
    slug: str,
) -> Category | None:
    statement = select(Category).where(Category.slug == slug)
    return db.scalar(statement)

def list_admin_categories(db: Session) -> list[Category]:
    statement = select(Category).order_by(Category.created_at.desc())
    return list(db.scalars(statement).all())

def get_category_by_id(
    db: Session,
    category_id: uuid.UUID,
) -> Category | None:
    statement = select(Category).where(Category.id == category_id)
    return db.scalar(statement)

