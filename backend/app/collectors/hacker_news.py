from app.collectors.http import get_json
from app.schemas.report import SourceItem


def collect_hacker_news(query: str, limit: int, category: str = "pest_social") -> list[SourceItem]:
    data = get_json(
        "https://hn.algolia.com/api/v1/search",
        params={
            "query": query,
            "tags": "story",
            "hitsPerPage": limit,
        },
    )

    sources: list[SourceItem] = []
    for item in data.get("hits", []):
        title = item.get("title") or item.get("story_title") or "Hacker News discussion"
        url = item.get("url") or item.get("story_url") or f"https://news.ycombinator.com/item?id={item.get('objectID')}"

        sources.append(
            SourceItem(
                source_type="hacker_news",
                category=category,
                title=title,
                url=url,
                snippet=f"points={item.get('points', 0)}, comments={item.get('num_comments', 0)}",
                query=query,
                published_at=item.get("created_at"),
                raw={
                    "points": item.get("points", 0),
                    "comments": item.get("num_comments", 0),
                },
            )
        )

    return sources
