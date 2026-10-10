
import logging
import uuid
from typing import Annotated

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.media import MediaType
from app.models.user import User
from app.schemas.media import MediaResponse
from app.services.image_validation import (
    MAX_IMAGE_SIZE_BYTES,
    validate_image,
)
from app.services.media import (
    create_media,
    delete_media,
    get_media_by_id,
    is_media_in_use,
    list_media,
)
from app.services.r2_storage import (
    get_r2_bucket_name,
    get_r2_client,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/media",
    tags=["Admin Media"],
)


@router.post(
    "",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_admin_media(
    file: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    caption: Annotated[str | None, Form()] = None,
    alt_text: Annotated[str | None, Form()] = None,
) -> MediaResponse:
    content = await file.read(MAX_IMAGE_SIZE_BYTES + 1)

    try:
        image_format, mime_type, width, height = validate_image(content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    extensions = {
        "JPEG": "jpg",
        "PNG": "png",
        "WEBP": "webp",
    }

    original_filename = (
        (file.filename or "upload")
        .replace("\\", "/")
        .rsplit("/", 1)[-1]
        .strip()[:255]
        or "upload"
    )

    storage_key = f"images/{uuid.uuid4().hex}.{extensions[image_format]}"

    try:
        client = get_r2_client()
        bucket_name = get_r2_bucket_name()
    except RuntimeError as exc:
        logger.error("R2 configuration is incomplete: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image storage is not configured correctly.",
        ) from exc

    try:
        client.put_object(
            Bucket=bucket_name,
            Key=storage_key,
            Body=content,
            ContentType=mime_type,
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to upload image to R2.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Image storage upload failed.",
        ) from exc

    try:
        media = create_media(
            db=db,
            media_type=MediaType.IMAGE,
            storage_key=storage_key,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=len(content),
            width=width,
            height=height,
            caption=caption,
            alt_text=alt_text,
        )
    except Exception as exc:
        db.rollback()

        try:
            client.delete_object(
                Bucket=bucket_name,
                Key=storage_key,
            )
        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed to clean up R2 object after database failure. "
                "Storage key: %s",
                storage_key,
            )

        if isinstance(exc, SQLAlchemyError):
            logger.exception("Failed to save uploaded image metadata.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image metadata could not be saved.",
        ) from exc

    return MediaResponse.model_validate(media)


@router.get(
    "",
    response_model=list[MediaResponse],
)
def list_admin_media(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[MediaResponse]:
    return list_media(db=db)


@router.get(
    "/{media_id}",
    response_model=MediaResponse,
)
def get_admin_media(
    media_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> MediaResponse:
    media = get_media_by_id(
        db=db,
        media_id=media_id,
    )

    if media is None:
        raise ResourceNotFoundError("Media not found.")

    return media



@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_admin_media(
    media_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> Response:
    media = get_media_by_id(
        db=db,
        media_id=media_id,
    )

    if media is None:
        raise ResourceNotFoundError("Media not found.")

    if is_media_in_use(db=db, media_id=media.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Media is in use. Remove its references before deleting it.",
        )

    try:
        client = get_r2_client()
        bucket_name = get_r2_bucket_name()
    except RuntimeError as exc:
        logger.error("R2 configuration is incomplete: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image storage is not configured correctly.",
        ) from exc

    storage_key = media.storage_key

    try:
        delete_media(db=db, media=media)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to delete media metadata.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image metadata could not be deleted.",
        ) from exc

    try:
        client.delete_object(Bucket=bucket_name, Key=storage_key)
    except (BotoCoreError, ClientError) as exc:
        logger.exception(
            "Media metadata was deleted, but R2 cleanup failed. "
            "Storage key: %s",
            storage_key,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Media metadata was deleted, but image storage cleanup failed. "
                "Contact an administrator."
            ),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
