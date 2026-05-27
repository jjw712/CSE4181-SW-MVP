from datetime import date, timedelta
import re

from app.collectors.http import get_json, post_json
from app.schemas.report import SourceItem


def collect_naver_search(
    query: str,
    category: str,
    endpoint: str,
    client_id: str,
    client_secret: str,
    limit: int,
) -> list[SourceItem]:
    data = get_json(
        f"https://openapi.naver.com/v1/search/{endpoint}.json",
        params={
            "query": query,
            "display": limit,
            "sort": "sim",
        },
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        },
    )

    sources: list[SourceItem] = []
    for item in data.get("items", []):
        sources.append(
            SourceItem(
                source_type=f"naver_{endpoint}",
                category=category,
                title=_clean_html(item.get("title") or "Naver result"),
                url=item.get("link") or item.get("originallink") or "",
                snippet=_clean_html(item.get("description") or ""),
                query=query,
                published_at=item.get("pubDate"),
                raw={"endpoint": endpoint},
            )
        )

    return sources


def collect_naver_datalab(
    queries: list[str],
    client_id: str,
    client_secret: str,
) -> list[SourceItem]:
    today = date.today()
    start = today - timedelta(days=30)
    keyword_groups = [
        {
            "groupName": query[:20],
            "keywords": [query],
        }
        for query in queries[:5]
    ]

    data = post_json(
        "https://openapi.naver.com/v1/datalab/search",
        payload={
            "startDate": start.isoformat(),
            "endDate": today.isoformat(),
            "timeUnit": "week",
            "keywordGroups": keyword_groups,
        },
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        },
    )

    sources: list[SourceItem] = []
    for item in data.get("results", []):
        values = [point.get("ratio", 0) for point in item.get("data", [])]
        avg_ratio = round(sum(values) / len(values), 2) if values else 0
        sources.append(
            SourceItem(
                source_type="naver_datalab",
                category="market",
                title=f"Naver DataLab: {item.get('title')}",
                url="https://datalab.naver.com/",
                snippet=f"최근 30일 평균 상대 관심도: {avg_ratio}",
                query=item.get("title") or "",
                raw={"average_ratio": avg_ratio, "points": item.get("data", [])},
            )
        )

    return sources


def _clean_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "").replace("&quot;", '"').replace("&amp;", "&")
