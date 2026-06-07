import json
import re
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote

from pydantic import ValidationError

from app.collectors.http import post_json
from app.core.config import Settings
from app.schemas.report import (
    GeneratedQueries,
    IdeaRequest,
    ReportBody,
    SourceItem,
)


GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
QUERY_CATEGORIES = (
    "customer_problem",
    "market",
    "competitors",
    "pricing",
    "implementation",
    "alternatives",
    "pest",
)

QUERY_PROMPT = """
너는 앱 아이디어 검증 리포트 플랫폼의 검색어 보강기다.
입력된 base_queries를 유지하면서 collector가 더 관련성 높은 자료를 찾도록 검색어를 보강한다.

규칙:
- JSON만 반환한다.
- 각 category별 추가 검색어는 최대 2개만 작성한다.
- 한국어 검색어를 우선하되 필요한 경우 짧은 영어 표현을 섞는다.
- 앱 성공 가능성, 시장 규모, 매출, 경쟁 우위는 추정하지 않는다.
- 문장형 설명이 아니라 검색에 바로 쓸 수 있는 짧은 phrase만 반환한다.

반환 형식:
{
  "generated_queries": {
    "customer_problem": [],
    "market": [],
    "competitors": [],
    "pricing": [],
    "implementation": [],
    "alternatives": [],
    "pest": []
  }
}
""".strip()

REPORT_PROMPT = """
너는 앱 아이디어 검증 리포트 작성기다.
제공된 sources만 근거로 한국어 JSON report를 작성한다.

중요 원칙:
- 앱 성공을 예측하거나 보장하지 않는다.
- 0~100 success score를 만들지 않는다.
- sources에 없는 시장 규모, 매출, 사용자 수, 경쟁 우위는 단정하지 않는다.
- evidence에는 반드시 제공된 source_id만 넣는다.
- 근거가 부족한 내용은 unverified 또는 unknowns에 넣는다.
- summary는 짧고 실무적으로 쓴다.
- competitors.items는 비워도 된다. 경쟁 앱 목록은 backend fallback 데이터로 병합된다.
- PEST는 별도 section이 아니라 risks/recommendation에 필요한 보조 신호로만 반영한다.

반환 형식:
{
  "idea_summary": {"summary": "", "evidence": [], "unverified": []},
  "target_users": {"summary": "", "evidence": [], "unverified": []},
  "related_keywords": {"summary": "", "keywords": [], "evidence": [], "unverified": []},
  "search_demand": {"summary": "", "evidence": [], "unverified": []},
  "competitors": {"items": [], "evidence": [], "unverified": []},
  "review_pain_points": {"summary": "", "evidence": [], "unverified": []},
  "monetization": {"summary": "", "evidence": [], "unverified": []},
  "mvp_scope": {
    "summary": "",
    "apis": [],
    "mvp_features": [],
    "technical_constraints": [],
    "evidence": [],
    "unverified": []
  },
  "risks": {"summary": "", "evidence": [], "unverified": []},
  "recommendation": {"summary": "", "evidence": [], "unverified": []},
  "data_confidence": {"summary": "", "evidence": [], "unverified": []},
  "unknowns": []
}
""".strip()


def is_llm_configured(settings: Settings) -> bool:
    return (
        settings.enable_llm
        and settings.llm_provider.lower() == "gemini"
        and bool(settings.gemini_api_key)
    )


def expand_queries_with_gemini(
    payload: IdeaRequest,
    base_queries: GeneratedQueries,
    settings: Settings,
) -> tuple[GeneratedQueries, bool, str | None]:
    if not is_llm_configured(settings):
        return base_queries, False, None

    request_payload = {
        "input": _compact_input(payload),
        "base_queries": base_queries.model_dump(),
    }

    try:
        response = _generate_json(
            prompt=QUERY_PROMPT,
            payload=request_payload,
            settings=settings,
            max_output_tokens=min(settings.llm_max_output_tokens, 400),
        )
        generated = response.get("generated_queries", response)
        return _merge_queries(base_queries, generated), True, None
    except Exception as error:
        return base_queries, False, _safe_error_message(error)


def summarize_report_with_gemini(
    payload: IdeaRequest,
    queries: GeneratedQueries,
    sources: list[SourceItem],
    fallback_report: ReportBody,
    settings: Settings,
) -> tuple[ReportBody, bool, str | None]:
    if not is_llm_configured(settings):
        return fallback_report, False, None

    compact_sources = _compact_sources(sources, settings)
    if not compact_sources:
        return fallback_report, False, None

    request_payload = {
        "input": _compact_input(payload),
        "generated_queries": _limit_queries(queries).model_dump(),
        "sources": compact_sources,
    }

    try:
        response = _generate_json(
            prompt=REPORT_PROMPT,
            payload=request_payload,
            settings=settings,
            max_output_tokens=settings.llm_max_output_tokens,
        )
        report_payload = response.get("report", response)
        llm_report = ReportBody.model_validate(report_payload)
        merged_report = _merge_report(fallback_report, llm_report)
        return _filter_unknown_evidence(merged_report, sources), True, None
    except (ValidationError, ValueError, TypeError, KeyError) as error:
        return fallback_report, False, _safe_error_message(error)
    except Exception as error:
        return fallback_report, False, _safe_error_message(error)


def _generate_json(
    prompt: str,
    payload: dict[str, Any],
    settings: Settings,
    max_output_tokens: int,
) -> dict[str, Any]:
    response = post_json(
        _gemini_url(settings),
        {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"{prompt}\n\n"
                                f"INPUT_JSON:\n{json.dumps(payload, ensure_ascii=False)}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": max_output_tokens,
                "responseMimeType": "application/json",
                "thinkingConfig": {"thinkingBudget": 0},
            },
        },
        headers={"x-goog-api-key": settings.gemini_api_key or ""},
        timeout=20,
    )
    text = _extract_text(response)
    parsed = _parse_json_text(text)
    if not isinstance(parsed, dict):
        raise ValueError("Gemini response JSON is not an object")
    return parsed


def _gemini_url(settings: Settings) -> str:
    model = settings.gemini_model.removeprefix("models/")
    return f"{GEMINI_API_BASE_URL}/{quote(model, safe='')}:generateContent"


def _extract_text(response: dict[str, Any]) -> str:
    candidates = response.get("candidates") or []
    for candidate in candidates:
        parts = candidate.get("content", {}).get("parts") or []
        text = "".join(str(part.get("text", "")) for part in parts if part.get("text"))
        if text.strip():
            return text

    raise ValueError("Gemini response does not contain text")


def _parse_json_text(text: str) -> Any:
    cleaned = _strip_code_fence(text.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])


def _strip_code_fence(text: str) -> str:
    if not text.startswith("```"):
        return text

    cleaned = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s*```$", "", cleaned).strip()


def _compact_input(payload: IdeaRequest) -> dict[str, str]:
    return {
        "idea": payload.idea,
        "target_customer": payload.target_customer,
        "region": payload.region,
        "service_type": payload.service_type,
    }


def _compact_sources(sources: list[SourceItem], settings: Settings) -> list[dict[str, Any]]:
    limit = max(1, settings.llm_max_input_sources)
    selected = _select_diverse_sources(sources, limit)
    return [
        {
            "source_id": source.source_id,
            "source_type": source.source_type,
            "category": source.category,
            "title": _clip(source.title, 140),
            "snippet": _clip(source.snippet, settings.llm_max_chars_per_source),
            "relevance_score": source.raw.get("relevance_score", 0),
        }
        for source in selected
    ]


def _select_diverse_sources(sources: list[SourceItem], limit: int) -> list[SourceItem]:
    selected: list[SourceItem] = []
    selected_ids: set[str] = set()
    seen_categories: set[str] = set()

    for source in sources:
        if source.category in seen_categories:
            continue
        selected.append(source)
        selected_ids.add(source.source_id)
        seen_categories.add(source.category)
        if len(selected) >= limit:
            return selected

    for source in sources:
        if source.source_id in selected_ids:
            continue
        selected.append(source)
        selected_ids.add(source.source_id)
        if len(selected) >= limit:
            break

    return selected


def _limit_queries(queries: GeneratedQueries) -> GeneratedQueries:
    data = {category: getattr(queries, category)[:4] for category in QUERY_CATEGORIES}
    return GeneratedQueries(**data)


def _merge_queries(base_queries: GeneratedQueries, additions: Any) -> GeneratedQueries:
    if not isinstance(additions, dict):
        return base_queries

    merged: dict[str, list[str]] = {}
    for category in QUERY_CATEGORIES:
        merged[category] = _dedupe(
            [
                *getattr(base_queries, category),
                *_as_string_list(additions.get(category)),
            ],
            limit=6,
        )

    return GeneratedQueries(**merged)


def _merge_report(fallback_report: ReportBody, llm_report: ReportBody) -> ReportBody:
    return llm_report.model_copy(
        update={
            "related_keywords": llm_report.related_keywords.model_copy(
                update={
                    "keywords": llm_report.related_keywords.keywords
                    or fallback_report.related_keywords.keywords,
                    "unverified": llm_report.related_keywords.unverified
                    or fallback_report.related_keywords.unverified,
                }
            ),
            "competitors": llm_report.competitors.model_copy(
                update={
                    "items": fallback_report.competitors.items,
                    "evidence": llm_report.competitors.evidence
                    or fallback_report.competitors.evidence,
                    "unverified": llm_report.competitors.unverified
                    or fallback_report.competitors.unverified,
                }
            ),
            "mvp_scope": llm_report.mvp_scope.model_copy(
                update={
                    "summary": llm_report.mvp_scope.summary
                    or fallback_report.mvp_scope.summary,
                    "apis": llm_report.mvp_scope.apis or fallback_report.mvp_scope.apis,
                    "mvp_features": llm_report.mvp_scope.mvp_features
                    or fallback_report.mvp_scope.mvp_features,
                    "technical_constraints": llm_report.mvp_scope.technical_constraints
                    or fallback_report.mvp_scope.technical_constraints,
                    "evidence": llm_report.mvp_scope.evidence
                    or fallback_report.mvp_scope.evidence,
                    "unverified": llm_report.mvp_scope.unverified
                    or fallback_report.mvp_scope.unverified,
                }
            ),
            "data_confidence": fallback_report.data_confidence,
            "unknowns": llm_report.unknowns or fallback_report.unknowns,
        }
    )


def _filter_unknown_evidence(report: ReportBody, sources: list[SourceItem]) -> ReportBody:
    valid_ids = {source.source_id for source in sources}

    return report.model_copy(
        update={
            "idea_summary": _filter_report_section(report.idea_summary, valid_ids),
            "target_users": _filter_report_section(report.target_users, valid_ids),
            "related_keywords": _filter_report_section(report.related_keywords, valid_ids),
            "search_demand": _filter_report_section(report.search_demand, valid_ids),
            "competitors": report.competitors.model_copy(
                update={
                    "evidence": _only_valid_ids(report.competitors.evidence, valid_ids),
                }
            ),
            "review_pain_points": _filter_report_section(report.review_pain_points, valid_ids),
            "monetization": _filter_report_section(report.monetization, valid_ids),
            "mvp_scope": report.mvp_scope.model_copy(
                update={
                    "evidence": _only_valid_ids(report.mvp_scope.evidence, valid_ids),
                }
            ),
            "risks": _filter_report_section(report.risks, valid_ids),
            "recommendation": _filter_report_section(report.recommendation, valid_ids),
            "data_confidence": _filter_report_section(report.data_confidence, valid_ids),
        }
    )


def _filter_report_section(section: Any, valid_ids: set[str]) -> Any:
    return section.model_copy(update={"evidence": _only_valid_ids(section.evidence, valid_ids)})


def _only_valid_ids(values: list[str], valid_ids: set[str]) -> list[str]:
    return [value for value in values if value in valid_ids]


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _dedupe(values: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = re.sub(r"\s+", " ", value or "").strip()
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def _clip(value: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    cleaned = re.sub(r"\s+", " ", value or "").strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[: max_chars - 1]}..."


def _safe_error_message(error: Exception) -> str:
    if isinstance(error, HTTPError):
        body = _read_http_error_body(error)
        message = f"HTTPError {error.code}: {body or error.reason}"
    else:
        message = f"{error.__class__.__name__}: {error}"
    return message[:240]


def _read_http_error_body(error: HTTPError) -> str:
    try:
        return error.read().decode("utf-8")[:180]
    except Exception:
        return ""
