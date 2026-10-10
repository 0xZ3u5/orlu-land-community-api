from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.schemas.home import HomeResponse
from app.services.home import get_home_data
from app.services.featured_media_responses import serialize_home_data

router = APIRouter(prefix="/home", tags=["Public Home"])


@router.get("", response_model=HomeResponse)
def get_home(
    db: Annotated[Session, Depends(get_db)],
) -> HomeResponse:
    home_data = get_home_data(db=db)

    if home_data["site"] is None:
        raise ResourceNotFoundError("Site settings not found.")

    return serialize_home_data(db, home_data)
