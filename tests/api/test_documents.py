from io import BytesIO
from unittest.mock import Mock

import pytest

from app.models.document import Document, DocumentStatus


PDF_CONTENT = b"%PDF-1.4\nTest PDF content\n%%EOF\n"


def add_document(db_session, status=DocumentStatus.DRAFT):
    document = Document(
        title="Community Application Form",
        description="Application form",
        storage_key="documents/test-application.pdf",
        original_filename="application-form.pdf",
        mime_type="application/pdf",
        file_size=len(PDF_CONTENT),
        status=status,
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


def test_upload_pdf_creates_draft_and_uploads_to_r2(client, db_session, monkeypatch):
    r2 = Mock()
    monkeypatch.setattr("app.api.v1.admin.documents.get_r2_client", lambda: r2)
    monkeypatch.setattr(
        "app.api.v1.admin.documents.get_r2_bucket_name",
        lambda: "test-bucket",
    )

    response = client.post(
        "/api/v1/admin/documents",
        data={
            "title": "Application Form",
            "description": "Download and complete this form.",
        },
        files={
            "file": (
                "../../application-form.pdf",
                PDF_CONTENT,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Application Form"
    assert payload["description"] == "Download and complete this form."
    assert payload["original_filename"] == "application-form.pdf"
    assert payload["mime_type"] == "application/pdf"
    assert payload["file_size"] == len(PDF_CONTENT)
    assert payload["status"] == "draft"

    r2.put_object.assert_called_once()
    upload_args = r2.put_object.call_args.kwargs
    assert upload_args["Bucket"] == "test-bucket"
    assert upload_args["Key"].startswith("documents/")
    assert upload_args["Body"] == PDF_CONTENT
    assert upload_args["ContentType"] == "application/pdf"

    saved = db_session.get(Document, payload["id"])
    assert saved is not None
    assert saved.status == DocumentStatus.DRAFT


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b"not a PDF",
        b"%PDF-1.4\nmissing EOF marker",
    ],
)
def test_upload_rejects_invalid_pdf_before_r2(client, monkeypatch, content):
    def unexpected_r2_call():
        raise AssertionError("R2 must not be called for an invalid PDF.")

    monkeypatch.setattr(
        "app.api.v1.admin.documents.get_r2_client",
        unexpected_r2_call,
    )

    response = client.post(
        "/api/v1/admin/documents",
        data={"title": "Invalid document"},
        files={"file": ("invalid.pdf", content, "application/pdf")},
    )

    assert response.status_code == 400


def test_public_listing_contains_only_published_documents(
    client, db_session
):
    draft = add_document(db_session, DocumentStatus.DRAFT)

    published = Document(
        title="Published Form",
        description=None,
        storage_key="documents/published-form.pdf",
        original_filename="published-form.pdf",
        mime_type="application/pdf",
        file_size=len(PDF_CONTENT),
        status=DocumentStatus.PUBLISHED,
    )
    db_session.add(published)
    db_session.commit()
    db_session.refresh(published)

    response = client.get("/api/v1/documents")

    assert response.status_code == 200
    payload = response.json()
    returned_ids = {item["id"] for item in payload}

    assert str(published.id) in returned_ids
    assert str(draft.id) not in returned_ids
    assert len(payload) == 1
    assert payload[0]["download_url"] == (
        f"/api/v1/documents/{published.id}/download"
    )


def test_unpublished_document_cannot_be_downloaded(
    client, db_session, monkeypatch
):
    document = add_document(db_session, DocumentStatus.DRAFT)

    def unexpected_r2_call():
        raise AssertionError("R2 must not be called for an unpublished document.")

    monkeypatch.setattr(
        "app.api.v1.public.documents.get_r2_client",
        unexpected_r2_call,
    )

    response = client.get(
        f"/api/v1/documents/{document.id}/download"
    )

    assert response.status_code == 404


def test_published_document_downloads_as_pdf(
    client, db_session, monkeypatch
):
    document = add_document(db_session, DocumentStatus.PUBLISHED)
    r2 = Mock()
    r2.get_object.return_value = {"Body": BytesIO(PDF_CONTENT)}

    monkeypatch.setattr(
        "app.api.v1.public.documents.get_r2_client",
        lambda: r2,
    )
    monkeypatch.setattr(
        "app.api.v1.public.documents.get_r2_bucket_name",
        lambda: "test-bucket",
    )

    response = client.get(
        f"/api/v1/documents/{document.id}/download"
    )

    assert response.status_code == 200
    assert response.content == PDF_CONTENT
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cache-control"] == "no-store"
    assert "attachment" in response.headers["content-disposition"]

    r2.get_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=document.storage_key,
    )


def test_admin_can_publish_and_withdraw_document(client, db_session):
    document = add_document(db_session, DocumentStatus.DRAFT)

    publish_response = client.post(
        f"/api/v1/admin/documents/{document.id}/publish"
    )
    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"

    withdraw_response = client.post(
        f"/api/v1/admin/documents/{document.id}/withdraw"
    )
    assert withdraw_response.status_code == 200
    assert withdraw_response.json()["status"] == "withdrawn"

    db_session.expire_all()
    saved = db_session.get(Document, document.id)
    assert saved.status == DocumentStatus.WITHDRAWN
