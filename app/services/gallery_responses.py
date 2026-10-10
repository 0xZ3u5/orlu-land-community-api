from app.schemas.gallery import GalleryImageResponse
from app.services.r2_storage import get_public_media_url


def serialize_gallery_items(items):
    return [
        GalleryImageResponse(
            media_id=media.id,
            sort_order=sort_order,
            public_url=get_public_media_url(media.storage_key),
            caption=media.caption,
            alt_text=media.alt_text,
            width=media.width,
            height=media.height,
            mime_type=media.mime_type,
        )
        for media, sort_order in items
    ]
