"""
Photo compression utility for wisata and desa photos
Compresses Base64 images to reduce size while maintaining quality
"""

import base64
import io
import re
from binascii import Error as Base64Error
from fastapi import HTTPException
from PIL import Image

ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
DATA_URI_PATTERN = re.compile(
    r"^data:(?P<mime>image/(?:jpeg|png|webp));base64,(?P<data>[A-Za-z0-9+/=\s]+)$",
    re.IGNORECASE,
)
MAX_IMAGE_BYTES = 5 * 1024 * 1024
TRUSTED_IMPORT_MAX_IMAGE_BYTES = 25 * 1024 * 1024


def _extract_image_payload(base64_string, max_input_bytes=MAX_IMAGE_BYTES):
    if not base64_string:
        return None

    value = base64_string.strip()
    mime_type = "image/jpeg"

    if value.startswith("data:"):
        match = DATA_URI_PATTERN.match(value)
        if not match:
            raise HTTPException(
                status_code=400,
                detail="Invalid image format. Use JPEG, PNG, or WebP.",
            )
        mime_type = match.group("mime").lower()
        value = match.group("data")

    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    compact_value = re.sub(r"\s+", "", value)
    estimated_size = len(compact_value) * 3 / 4
    if estimated_size > max_input_bytes:
        max_mb = max_input_bytes // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"Image exceeds {max_mb} MB limit")

    try:
        return base64.b64decode(compact_value, validate=True)
    except (Base64Error, ValueError):
        raise HTTPException(status_code=400, detail="Invalid image data")


def compress_base64_image(
    base64_string,
    max_width=1200,
    quality=85,
    max_input_bytes=MAX_IMAGE_BYTES,
):
    """
    Compress a Base64 encoded image

    Args:
        base64_string: Base64 encoded image string (with or without data URI prefix)
        max_width: Maximum width in pixels (default 1200px)
        quality: JPEG quality 1-100 (default 85)

    Returns:
        Compressed Base64 string with data URI prefix
    """
    if not base64_string:
        return None

    try:
        image_data = _extract_image_payload(base64_string, max_input_bytes)

        # Open image with Pillow
        image = Image.open(io.BytesIO(image_data))
        image.verify()
        image = Image.open(io.BytesIO(image_data))

        # Convert to RGB if necessary (handles PNG with transparency)
        if image.mode in ("RGBA", "LA", "P"):
            # Create white background
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(
                image, mask=image.split()[-1] if image.mode == "RGBA" else None
            )
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Resize if width exceeds max_width
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Compress and save to bytes
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
        output.seek(0)

        # Encode back to Base64
        compressed_base64 = base64.b64encode(output.read()).decode("utf-8")

        # Add data URI prefix
        return f"data:image/jpeg;base64,{compressed_base64}"

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")


def get_image_size_kb(base64_string, max_input_bytes=TRUSTED_IMPORT_MAX_IMAGE_BYTES):
    """Get the size of a Base64 image in KB"""
    if not base64_string:
        return 0
    image_data = _extract_image_payload(base64_string, max_input_bytes)
    return len(image_data) / 1024
