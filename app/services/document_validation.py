MAX_DOCUMENT_SIZE_BYTES = 20 * 1024 * 1024
PDF_MIME_TYPE = "application/pdf"


def validate_pdf(content: bytes) -> None:
    """Perform basic PDF signature, size, and EOF-marker checks."""
    if not content:
        raise ValueError("The uploaded file is empty.")

    if len(content) > MAX_DOCUMENT_SIZE_BYTES:
        raise ValueError("PDF size must not exceed 20 MiB.")

    if not content.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    if b"%%EOF" not in content[-2048:]:
        raise ValueError("The uploaded file appears to be an incomplete PDF.")
