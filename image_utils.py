"""
Photo compression utility for wisata and desa photos
Compresses Base64 images to reduce size while maintaining quality
"""

import base64
import io
from PIL import Image


def compress_base64_image(base64_string, max_width=1200, quality=85):
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
        # Remove data URI prefix if present
        if base64_string.startswith("data:image"):
            base64_string = base64_string.split(",")[1]

        # Decode Base64 to bytes
        image_data = base64.b64decode(base64_string)

        # Open image with Pillow
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

    except Exception as e:
        print(f"Error compressing image: {e}")
        return base64_string  # Return original if compression fails


def get_image_size_kb(base64_string):
    """Get the size of a Base64 image in KB"""
    if not base64_string:
        return 0
    if base64_string.startswith("data:image"):
        base64_string = base64_string.split(",")[1]
    return len(base64_string) * 3 / 4 / 1024  # Base64 to bytes to KB
