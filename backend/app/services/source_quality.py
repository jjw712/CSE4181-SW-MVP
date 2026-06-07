import re

from app.schemas.report import IdeaRequest, SourceItem


ALWAYS_KEEP_TYPES = {"apple_itunes", "naver_datalab"}
STOPWORDS = {
    "앱",
    "서비스",
    "모바일",
    "한국",
    "시장",
    "트렌드",
    "수요",
    "관리",
    "사용자",
    "문제",
}


def annotate_source_relevance(payload: IdeaRequest, sources: list[SourceItem]) -> list[SourceItem]:
    tokens = _tokens(f"{payload.idea} {payload.target_customer} {payload.service_type}")
    annotated = [_annotate(source, tokens) for source in sources]
    return sorted(annotated, key=_sort_key)


def _annotate(source: SourceItem, tokens: set[str]) -> SourceItem:
    text = f"{source.title} {source.snippet} {source.query}".lower()
    matches = sorted(token for token in tokens if token.lower() in text)
    score = len(matches)

    if source.source_type in ALWAYS_KEEP_TYPES:
        score += 2
    if source.category == "competitors":
        score += 1
    if source.category == "market":
        score += 1

    raw = {
        **source.raw,
        "relevance_score": score,
        "relevance_matches": matches[:8],
    }
    return source.model_copy(update={"raw": raw})


def _sort_key(source: SourceItem) -> tuple[int, int, str]:
    score = int(source.raw.get("relevance_score", 0))
    category_priority = {
        "market": 0,
        "competitors": 1,
        "customer_problem": 2,
        "pest_technological": 3,
        "pest_social": 4,
        "pest_economic": 5,
        "pest_political": 6,
    }.get(source.category, 9)
    return (-score, category_priority, source.source_id)


def _tokens(value: str) -> set[str]:
    result: set[str] = set()
    for token in re.findall(r"[0-9A-Za-z가-힣]+", value):
        normalized = token.strip().lower()
        if len(normalized) < 2 or normalized in STOPWORDS:
            continue
        result.add(normalized)
    return result
