import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.page import Page


ALLOWED_PAGE_SLUGS = {"about", "contact"}


def get_page_by_slug(
    db: Session,
    *,
    slug: str,
) -> Page | None:
    if slug not in ALLOWED_PAGE_SLUGS:
        return None

    statement = select(Page).where(Page.slug == slug)
    return db.scalar(statement)


def update_page(
    db: Session,
    *,
    page: Page,
    title: str,
    content: str,
) -> Page:
    page.title = title
    page.content = content

    db.commit()
    db.refresh(page)

    return page
