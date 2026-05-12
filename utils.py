import html


def sanitize_html(text):
    """Escape HTML special characters to prevent XSS attacks"""
    if text is None:
        return None
    return html.escape(str(text))


def sanitize_dict(data):
    """Recursively sanitize all string values in a dictionary"""
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    elif isinstance(data, str):
        return sanitize_html(data)
    return data
