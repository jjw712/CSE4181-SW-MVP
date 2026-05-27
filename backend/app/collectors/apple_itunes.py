from app.collectors.http import get_json
from app.schemas.report import SourceItem


def collect_apple_itunes(
    query: str,
    region: str,
    limit: int,
) -> list[SourceItem]:
    data = get_json(
        "https://itunes.apple.com/search",
        params={
            "term": query,
            "country": _country_code(region),
            "entity": "software",
            "limit": limit,
        },
    )

    sources: list[SourceItem] = []
    for item in data.get("results", []):
        name = item.get("trackName") or item.get("trackCensoredName") or "Unknown app"
        category = item.get("primaryGenreName") or ""
        rating = item.get("averageUserRating")
        review_count = item.get("userRatingCount")
        price = _format_price(item)
        snippet_parts = [part for part in [category, price, _rating_text(rating, review_count)] if part]

        sources.append(
            SourceItem(
                source_type="apple_itunes",
                category="competitors",
                title=name,
                url=item.get("trackViewUrl") or "",
                snippet=" / ".join(snippet_parts),
                query=query,
                raw={
                    "app_name": name,
                    "category": category or None,
                    "rating": rating,
                    "review_count": review_count,
                    "price": price,
                },
            )
        )

    return sources


def _country_code(region: str) -> str:
    normalized = (region or "").lower()
    if "미국" in normalized or "us" in normalized or "global" in normalized:
        return "US"
    return "KR"


def _format_price(item: dict) -> str:
    if item.get("formattedPrice"):
        return str(item["formattedPrice"])

    price = item.get("price")
    currency = item.get("currency") or ""
    if price in (0, 0.0, "0"):
        return "Free"
    if price is not None:
        return f"{price} {currency}".strip()
    return "Unknown"


def _rating_text(rating: float | None, review_count: int | None) -> str:
    if rating is None and review_count is None:
        return ""
    if rating is None:
        return f"{review_count} ratings"
    if review_count is None:
        return f"{rating:.1f} rating"
    return f"{rating:.1f} rating / {review_count} ratings"
