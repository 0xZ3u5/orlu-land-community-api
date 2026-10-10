from io import BytesIO
import warnings

from PIL import Image, UnidentifiedImageError


MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

ALLOWED_IMAGE_FORMATS = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


def validate_image(content: bytes) -> tuple[str, str, int, int]:
    """Validate image bytes and return (format, MIME type, width, height)."""
    if not content:
        raise ValueError("The uploaded file is empty.")

    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise ValueError("Image size must not exceed 10 MiB.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(BytesIO(content)) as image:
                image_format = image.format

                if image_format not in ALLOWED_IMAGE_FORMATS:
                    raise ValueError(
                        "Unsupported image format. "
                        "Allowed formats: JPEG, PNG, WebP."
                    )

                image.verify()

            # Reopen after verify() to safely read the image dimensions.
            with Image.open(BytesIO(content)) as image:
                width, height = image.size

                if width <= 0 or height <= 0:
                    raise ValueError("Image dimensions are invalid.")

    except ValueError:
        raise
    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        SyntaxError,
    ) as exc:
        raise ValueError("The uploaded file is not a valid, safe image.") from exc

    return (
        image_format,
        ALLOWED_IMAGE_FORMATS[image_format],
        width,
        height,
    )
