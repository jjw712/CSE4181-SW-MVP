from app.collectors.http import get_json
from app.schemas.report import SourceItem


def collect_github_repositories(
    query: str,
    limit: int,
    token: str | None = None,
) -> list[SourceItem]:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = get_json(
        "https://api.github.com/search/repositories",
        params={
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": limit,
        },
        headers=headers,
    )

    sources: list[SourceItem] = []
    for item in data.get("items", []):
        sources.append(
            SourceItem(
                source_type="github",
                category="pest_technological",
                title=item.get("full_name") or item.get("name") or "GitHub repository",
                url=item.get("html_url") or "",
                snippet=item.get("description") or "",
                query=query,
                published_at=item.get("updated_at"),
                raw={
                    "stars": item.get("stargazers_count", 0),
                    "language": item.get("language"),
                },
            )
        )

    return sources
