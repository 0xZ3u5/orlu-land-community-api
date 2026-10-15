import logging
import uuid
from urllib.parse import quote

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.errors import ResourceNotFoundError
from app.db.session import get_db
from app.models.document import DocumentStatus
from app.schemas.document import PublicDocumentResponse
from app.services.documents import get_document_by_id, list_documents
from app.services.r2_storage import get_r2_bucket_name, get_r2_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Public Documents"])


@router.get("", response_model=list[PublicDocumentResponse])
def list_public_documents(
    db: Session = Depends(get_db),
) -> list[PublicDocumentResponse]:
    documents = list_documents(db=db, published_only=True)
    return [
        PublicDocumentResponse(
            id=document.id,
            title=document.title,
            description=document.description,
            file_size=document.file_size,
            created_at=document.created_at,
            download_url=f"/api/v1/documents/{document.id}/download",
        )
        for document in documents
    ]


@router.get("/{document_id}/download")
def download_public_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Response:
    document = get_document_by_id(db=db, document_id=document_id)
    if document is None or document.status != DocumentStatus.PUBLISHED:
        raise ResourceNotFoundError("Published document not found.")

    try:
        client = get_r2_client()
        bucket = get_r2_bucket_name()
        stored_object = client.get_object(Bucket=bucket, Key=document.storage_key)
        content = stored_object["Body"].read()
    except RuntimeError as exc:
        logger.error("R2 configuration is incomplete: %s", exc)
        raise HTTPException(status_code=503, detail="Document storage is unavailable.") from exc
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to retrieve PDF from R2.")
        raise HTTPException(status_code=502, detail="Document download failed.") from exc

    filename = quote(document.original_filename or "document.pdf", safe="")
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-store",
        },
    )
