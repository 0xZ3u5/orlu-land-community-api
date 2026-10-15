import logging
import uuid
from typing import Annotated
from urllib.parse import quote

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.document import DocumentStatus
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentUpdate
from app.services.document_validation import (
    MAX_DOCUMENT_SIZE_BYTES,
    validate_pdf,
)
from app.services.documents import (
    create_document,
    get_document_by_id,
    list_documents,
    update_document,
)
from app.services.r2_storage import get_r2_bucket_name, get_r2_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/documents", tags=["Admin Documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form(min_length=1, max_length=255)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    description: Annotated[str | None, Form()] = None,
) -> DocumentResponse:
    title = title.strip()
    if not title:
        raise HTTPException(
            status_code=422,
            detail="Title cannot be blank.",
        )
    content = await file.read(MAX_DOCUMENT_SIZE_BYTES + 1)

    try:
        validate_pdf(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await file.close()

    original_filename = (
        (file.filename or "document.pdf")
        .replace("\\", "/")
        .rsplit("/", 1)[-1]
        .replace("\r", "")
        .replace("\n", "")
        .strip()[:255]
        or "document.pdf"
    )
    storage_key = f"documents/{uuid.uuid4().hex}.pdf"

    try:
        client = get_r2_client()
        bucket = get_r2_bucket_name()
    except RuntimeError as exc:
        logger.error("R2 configuration is incomplete: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Document storage is not configured correctly.",
        ) from exc

    try:
        client.put_object(
            Bucket=bucket,
            Key=storage_key,
            Body=content,
            ContentType="application/pdf",
            ContentDisposition='attachment; filename="document.pdf"',
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to upload PDF to R2.")
        raise HTTPException(
            status_code=502,
            detail="Document storage upload failed.",
        ) from exc

    try:
        document = create_document(
            db=db,
            title=title.strip(),
            description=description,
            storage_key=storage_key,
            original_filename=original_filename,
            file_size=len(content),
        )
    except Exception as exc:
        db.rollback()
        try:
            client.delete_object(Bucket=bucket, Key=storage_key)
        except (BotoCoreError, ClientError):
            logger.exception("Failed to clean up PDF after database failure: %s", storage_key)
        if isinstance(exc, SQLAlchemyError):
            logger.exception("Failed to save document metadata.")
        raise HTTPException(
            status_code=500,
            detail="Document metadata could not be saved.",
        ) from exc

    return document


@router.get("", response_model=list[DocumentResponse])
def list_admin_documents(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[DocumentResponse]:
    return list_documents(db=db)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_admin_document(
    document_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> DocumentResponse:
    document = get_document_by_id(db=db, document_id=document_id)
    if document is None:
        raise ResourceNotFoundError("Document not found.")
    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
def patch_admin_document(
    document_id: uuid.UUID,
    data: DocumentUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> DocumentResponse:
    document = get_document_by_id(db=db, document_id=document_id)
    if document is None:
        raise ResourceNotFoundError("Document not found.")

    if "title" in data.model_fields_set and data.title is None:
        raise HTTPException(status_code=422, detail="Title cannot be null.")

    if data.title is not None and not data.title.strip():
        raise HTTPException(status_code=422, detail="Title cannot be blank.")

    try:
        return update_document(
            db=db,
            document=document,
            title=data.title,
            description=data.description,
            description_provided="description" in data.model_fields_set,
            status=data.status,
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to update document metadata.")
        raise HTTPException(status_code=500, detail="Document update failed.") from exc


@router.post("/{document_id}/publish", response_model=DocumentResponse)
def publish_document(
    document_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> DocumentResponse:
    document = get_document_by_id(db=db, document_id=document_id)
    if document is None:
        raise ResourceNotFoundError("Document not found.")
    return update_document(db=db, document=document, status=DocumentStatus.PUBLISHED)


@router.post("/{document_id}/withdraw", response_model=DocumentResponse)
def withdraw_document(
    document_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> DocumentResponse:
    document = get_document_by_id(db=db, document_id=document_id)
    if document is None:
        raise ResourceNotFoundError("Document not found.")
    return update_document(db=db, document=document, status=DocumentStatus.WITHDRAWN)
