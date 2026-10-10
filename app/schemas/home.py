from pydantic import BaseModel

from app.schemas.event import EventResponse
from app.schemas.post import PostResponse
from app.schemas.site import SiteResponse


class HomeResponse(BaseModel):
    site: SiteResponse
    featured_posts: list[PostResponse]
    latest_posts: list[PostResponse]
    upcoming_events: list[EventResponse]
