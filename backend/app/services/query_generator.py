import re

from app.schemas.report import GeneratedQueries, IdeaRequest


def generate_queries(payload: IdeaRequest) -> GeneratedQueries:
    idea = _clean(payload.idea)
    target = _clean(payload.target_customer) or "사용자"
    region = _clean(payload.region) or "한국"
    service_type = _clean(payload.service_type) or "앱"

    return GeneratedQueries(
        customer_problem=_dedupe(
            [
                f"{target} {idea} 불편",
                f"{target} {idea} 문제",
                f"{idea} 사용자 불만",
                f"{idea} pain point",
            ],
            limit=4,
        ),
        market=_dedupe(
            [
                f"{region} {idea} 시장",
                f"{idea} 트렌드",
                f"{idea} 수요",
                f"{idea} market trend",
            ],
            limit=4,
        ),
        competitors=_dedupe(
            [
                f"{idea} 앱",
                f"{idea} {service_type}",
                f"{idea} competitor app",
                f"{target} {idea} 서비스",
            ],
            limit=4,
        ),
        pricing=_dedupe(
            [
                f"{idea} 가격",
                f"{idea} 구독",
                f"{idea} freemium",
                f"{idea} pricing",
            ],
            limit=4,
        ),
        implementation=_dedupe(
            [
                f"{idea} API",
                f"{idea} 오픈소스",
                f"{idea} 구현",
                f"{idea} github",
            ],
            limit=4,
        ),
        alternatives=_dedupe(
            [
                f"{target} {idea} 대체재",
                f"{idea} 엑셀 템플릿",
                f"{idea} 노션 템플릿",
                f"{idea} workaround",
            ],
            limit=4,
        ),
        pest=_dedupe(
            [
                f"{region} {idea} 정책",
                f"{region} {idea} 시장 동향",
                f"{idea} 사용자 행동 변화",
                f"{idea} 기술 동향",
            ],
            limit=4,
        ),
    )


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _dedupe(values: list[str], limit: int) -> list[str]:
    seen = set()
    result = []
    for value in values:
        normalized = _clean(value)
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result
