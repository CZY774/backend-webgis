from math import ceil

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10


def paginate_query(query, page, limit, serializer=None):
    safe_limit = min(max(limit, 1), MAX_PAGE_SIZE)
    safe_page = max(page, 1)
    total = query.count()
    items = query.offset((safe_page - 1) * safe_limit).limit(safe_limit).all()

    if serializer:
        items = [serializer(item) for item in items]

    return {
        "items": items,
        "page": safe_page,
        "limit": safe_limit,
        "total": total,
        "total_pages": ceil(total / safe_limit) if total else 0,
    }
