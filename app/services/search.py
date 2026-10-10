import math

from sqlalchemy import DateTime, String, func, literal, select, union_all
from sqlalchemy.orm import Session

from app.models.event import Event, EventStatus
from app.models.post import Post, PostStatus


def search_content(
    db: Session,
    *,
    query: str,
    page: int,
    limit: int,
) -> tuple[list[dict], int]:
    search_query = query.strip()

    if not search_query:
        return [], 0

    offset = (page - 1) * limit

    post_search_vector = func.to_tsvector(
        "english",
        func.concat_ws(
            " ",
            Post.title,
            Post.excerpt,
            Post.content,
        ),
    )

    event_search_vector = func.to_tsvector(
        "english",
        func.concat_ws(
            " ",
            Event.title,
            Event.description,
        ),
    )

    ts_query = func.websearch_to_tsquery(
        "english",
        search_query,
    )

    post_query = select(
        literal("post").label("type"),
        Post.id.label("id"),
        Post.title.label("title"),
        Post.slug.label("slug"),
        Post.excerpt.label("excerpt"),
        literal(None, type_=DateTime(timezone=True)).label("start_at"),
        Post.published_at.label("published_at"),
        func.ts_rank(
            post_search_vector,
            ts_query,
        ).label("rank"),
    ).where(
        Post.status == PostStatus.PUBLISHED,
        Post.published_at <= func.now(),
        post_search_vector.op("@@")(ts_query),
    )

    event_query = select(
        literal("event").label("type"),
        Event.id.label("id"),
        Event.title.label("title"),
        Event.slug.label("slug"),
        literal(None, type_=String()).label("excerpt"),
        Event.start_at.label("start_at"),
        literal(None, type_=DateTime(timezone=True)).label("published_at"),
        func.ts_rank(
            event_search_vector,
            ts_query,
        ).label("rank"),
    ).where(
        Event.status == EventStatus.PUBLISHED,
        event_search_vector.op("@@")(ts_query),
    )

    combined_query = union_all(
        post_query,
        event_query,
    ).subquery()

    total_statement = select(
        func.count()
    ).select_from(combined_query)

    total = db.scalar(total_statement) or 0

    result_statement = (
        select(combined_query)
        .order_by(
            combined_query.c.rank.desc(),
            combined_query.c.title.asc(),
        )
        .offset(offset)
        .limit(limit)
    )

    rows = db.execute(result_statement).mappings().all()

    results = [
        {
            "type": row["type"],
            "id": row["id"],
            "title": row["title"],
            "slug": row["slug"],
            "excerpt": row["excerpt"],
            "start_at": row["start_at"],
            "published_at": row["published_at"],
        }
        for row in rows
    ]

    return results, total


def get_search_suggestions(
    db: Session,
    *,
    query: str,
    limit: int = 8,
) -> list[dict]:
    search_query = query.strip()

    if not search_query:
        return []

    pattern = f"{search_query}%"

    post_query = select(
        literal("post").label("type"),
        Post.id.label("id"),
        Post.title.label("title"),
        Post.slug.label("slug"),
    ).where(
        Post.status == PostStatus.PUBLISHED,
        Post.published_at <= func.now(),
        Post.title.ilike(pattern),
    )

    event_query = select(
        literal("event").label("type"),
        Event.id.label("id"),
        Event.title.label("title"),
        Event.slug.label("slug"),
    ).where(
        Event.status == EventStatus.PUBLISHED,
        Event.title.ilike(pattern),
    )

    combined_query = union_all(
        post_query,
        event_query,
    ).subquery()

    statement = (
        select(combined_query)
        .order_by(combined_query.c.title.asc())
        .limit(limit)
    )

    rows = db.execute(statement).mappings().all()

    return [
        {
            "type": row["type"],
            "id": row["id"],
            "title": row["title"],
            "slug": row["slug"],
        }
        for row in rows
    ]


def calculate_total_pages(
    total: int,
    limit: int,
) -> int:
    return math.ceil(total / limit) if total else 0
