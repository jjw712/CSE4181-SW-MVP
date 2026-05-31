import re
from threading import Lock
from time import monotonic
from typing import Any

from app.collectors.http import get_json
from app.schemas.report import SourceItem


GDELT_CACHE_TTL_SECONDS = 300
GDELT_MAX_ATTEMPTS = 3
GDELT_BACKOFF_SECONDS = 5.0

_cache: dict[tuple[str, int], tuple[float, dict[str, Any]]] = {}
_cache_lock = Lock()


def collect_gdelt(query: str, limit: int, category: str = "pest_economic") -> list[SourceItem]:
    data = _get_gdelt_data(query, limit)

    sources: list[SourceItem] = []
    for item in data.get("articles", []):
        sources.append(
            SourceItem(
                source_type="gdelt",
                category=category,
                title=item.get("title") or "GDELT article",
                url=item.get("url") or "",
                snippet=item.get("sourceCountry") or item.get("domain") or "",
                query=query,
                published_at=item.get("seendate"),
                raw={
                    "domain": item.get("domain"),
                    "source_country": item.get("sourceCountry"),
                    "language": item.get("language"),
                },
            )
        )

    return sources


def _get_gdelt_data(query: str, limit: int) -> dict[str, Any]:
    gdelt_query = _sanitize_gdelt_query(query)
    cache_key = (gdelt_query, limit)
    now = monotonic()

    with _cache_lock:
        cached = _cache.get(cache_key)
        if cached and now - cached[0] < GDELT_CACHE_TTL_SECONDS:
            return cached[1]

    data = get_json(
        "https://api.gdeltproject.org/api/v2/doc/doc",
        params={
            "query": gdelt_query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": limit,
            "sort": "HybridRel",
        },
        max_attempts=GDELT_MAX_ATTEMPTS,
        backoff_seconds=GDELT_BACKOFF_SECONDS,
        retry_on_url_error=True,
        retry_on_json_error=True,
    )

    with _cache_lock:
        _cache[cache_key] = (now, data)

    return data


def clear_gdelt_cache() -> None:
    with _cache_lock:
        _cache.clear()


def _sanitize_gdelt_query(query: str) -> str:
    tokens = re.findall(r"[^\W_]+", query, flags=re.UNICODE)
    filtered = [token for token in tokens if len(token) >= 2]
    return " ".join(filtered) or "market trend"
