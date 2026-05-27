from app.collectors.http import get_json
from app.schemas.report import SourceItem


def collect_gdelt(query: str, limit: int, category: str = "pest_economic") -> list[SourceItem]:
    data = get_json(
        "https://api.gdeltproject.org/api/v2/doc/doc",
        params={
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": limit,
            "sort": "HybridRel",
        },
    )

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
