from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import (
    SearchResponse,
    SearchResult,
    SearchSuggestion,
    SearchSuggestionsResponse,
)
from app.services.search import (
    calculate_total_pages,
    get_search_suggestions,
    search_content,
)

router = APIRouter(prefix="/search", tags=["Public Search"])


@router.get("", response_model=SearchResponse)
def search(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str, Query(min_length=1)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> SearchResponse:
    results, total = search_content(
        db=db,
        query=q,
        page=page,
        limit=limit,
    )

    return SearchResponse(
        query=q,
        page=page,
        limit=limit,
        total=total,
        total_pages=calculate_total_pages(total, limit),
        results=[
            SearchResult.model_validate(result)
            for result in results
        ],
    )


@router.get(
    "/suggestions",
    response_model=SearchSuggestionsResponse,
)
def search_suggestions(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str, Query(min_length=1)],
    limit: Annotated[int, Query(ge=1, le=10)] = 8,
) -> SearchSuggestionsResponse:
    suggestions = get_search_suggestions(
        db=db,
        query=q,
        limit=limit,
    )

    return SearchSuggestionsResponse(
        query=q,
        suggestions=[
            SearchSuggestion.model_validate(suggestion)
            for suggestion in suggestions
        ],
    )
