from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.gallery import GalleryImageResponse
from app.services.gallery import list_standalone_gallery
from app.services.gallery_responses import serialize_gallery_items

router = APIRouter(prefix="/gallery", tags=["Public Gallery"])


@router.get("", response_model=list[GalleryImageResponse])
def get_public_gallery(
    db: Annotated[Session, Depends(get_db)],
) -> list[GalleryImageResponse]:
    return serialize_gallery_items(list_standalone_gallery(db))
