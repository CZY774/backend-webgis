import html
import re


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return text

    # HTML escape
    text = html.escape(text)

    # Remove any remaining script tags
    text = re.sub(
        r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL
    )

    # Remove javascript: protocol
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)

    # Remove on* event handlers
    text = re.sub(r"\s*on\w+\s*=", "", text, flags=re.IGNORECASE)

    return text
