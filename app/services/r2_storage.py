import boto3
from botocore.config import Config

from app.core.config import settings


def get_r2_client():
    required_settings = {
        "R2_ENDPOINT_URL": settings.r2_endpoint_url,
        "R2_ACCESS_KEY_ID": settings.r2_access_key_id,
        "R2_SECRET_ACCESS_KEY": settings.r2_secret_access_key,
        "R2_BUCKET_NAME": settings.r2_bucket_name,
        "R2_PUBLIC_BASE_URL": settings.r2_public_base_url,
    }

    missing = [
        name for name, value in required_settings.items()
        if not value or not value.strip()
    ]

    if missing:
        raise RuntimeError(
            "Missing required R2 configuration: "
            + ", ".join(missing)
        )

    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url.rstrip("/"),
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )


def get_r2_bucket_name() -> str:
    if not settings.r2_bucket_name:
        raise RuntimeError("R2_BUCKET_NAME is not configured.")

    return settings.r2_bucket_name


def get_public_media_url(storage_key: str) -> str:
    base_url = settings.r2_public_base_url

    if not base_url or not base_url.strip():
        raise RuntimeError("R2_PUBLIC_BASE_URL is not configured.")

    return f"{base_url.rstrip('/')}/{storage_key.lstrip('/')}"
