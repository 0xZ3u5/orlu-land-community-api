import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus


def list_documents(
    db: Session,
    *,
    published_only: bool = False,
) -> list[Document]:
    statement = select(Document).order_by(Document.created_at.desc())

    if published_only:
        statement = statement.where(
            Document.status == DocumentStatus.PUBLISHED
        )

    return list(db.scalars(statement).all())


def get_document_by_id(
    db: Session,
    document_id: uuid.UUID,
) -> Document | None:
    return db.scalar(
        select(Document).where(Document.id == document_id)
    )


def create_document(
    db: Session,
    *,
    title: str,
    description: str | None,
    storage_key: str,
    original_filename: str,
    file_size: int,
) -> Document:
    document = Document(
        title=title,
        description=description,
        storage_key=storage_key,
        original_filename=original_filename,
        mime_type="application/pdf",
        file_size=file_size,
        status=DocumentStatus.DRAFT,
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document(
    db: Session,
    *,
    document: Document,
    title: str | None = None,
    description: str | None = None,
    description_provided: bool = False,
    status: DocumentStatus | None = None,
) -> Document:
    if title is not None:
        document.title = title.strip()

    if description_provided:
        document.description = description

    if status is not None:
        document.status = status

    db.commit()
    db.refresh(document)
    return document
