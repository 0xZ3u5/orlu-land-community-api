from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    type: Literal["post", "event"]
    id: UUID
    title: str
    slug: str
    excerpt: str | None = None
    start_at: datetime | None = None
    published_at: datetime | None = None


class SearchResponse(BaseModel):
    query: str
    page: int
    limit: int
    total: int
    total_pages: int
    results: list[SearchResult]


class SearchSuggestion(BaseModel):
    type: Literal["post", "event"]
    id: UUID
    title: str
    slug: str


class SearchSuggestionsResponse(BaseModel):
    query: str
    suggestions: list[SearchSuggestion]
