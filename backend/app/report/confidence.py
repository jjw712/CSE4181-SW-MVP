from app.schemas.report import ReportMeta, SourceItem


def calculate_confidence(
    sources: list[SourceItem],
    skipped_collectors: list[str],
    failed_collectors: list[str],
    collector_errors: dict[str, str],
    llm_used: bool,
    live_collectors_used: bool,
    llm_provider: str | None = None,
    llm_model: str | None = None,
    llm_error: str | None = None,
) -> ReportMeta:
    source_count = len(sources)
    source_types = {source.source_type for source in sources}
    categories = {source.category for source in sources}

    reasons: list[str] = [
        f"수집된 source {source_count}개",
        f"source type {len(source_types)}종",
    ]

    if "competitors" in categories:
        reasons.append("경쟁 앱 후보 데이터가 포함됨")
    else:
        reasons.append("경쟁 앱 데이터가 부족함")

    if "market" in categories:
        reasons.append("시장/검색 관심도 관련 데이터가 포함됨")
    else:
        reasons.append("시장/검색 관심도 데이터가 부족함")

    if failed_collectors:
        transient_failures = _transient_failures(failed_collectors, collector_errors)
        blocking_failures = [name for name in failed_collectors if name not in transient_failures]
        if blocking_failures:
            reasons.append(f"실패한 collector: {', '.join(blocking_failures)}")
        if transient_failures:
            reasons.append(f"일시적 요청 제한 collector: {', '.join(transient_failures)}")
    if skipped_collectors:
        reasons.append(f"건너뛴 collector: {', '.join(skipped_collectors)}")
    if llm_used:
        reasons.append("Gemini는 검색어 보강/출처 요약에만 사용됨")
    if llm_error:
        reasons.append("LLM 일부 단계는 fallback 처리됨")

    blocking_failure_count = len(failed_collectors) - len(_transient_failures(failed_collectors, collector_errors))
    if source_count >= 8 and len(source_types) >= 4 and blocking_failure_count == 0:
        level = "High"
    elif source_count >= 3 and len(source_types) >= 2:
        level = "Medium"
    else:
        level = "Low"

    return ReportMeta(
        confidence_level=level,
        confidence_reasons=reasons,
        llm_used=llm_used,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_error=llm_error,
        live_collectors_used=live_collectors_used,
        skipped_collectors=skipped_collectors,
        failed_collectors=failed_collectors,
        collector_errors=collector_errors,
    )


def _transient_failures(
    failed_collectors: list[str],
    collector_errors: dict[str, str],
) -> list[str]:
    transient: list[str] = []
    for name in failed_collectors:
        message = collector_errors.get(name, "")
        if "HTTP Error 429" in message or "HTTPError 429" in message:
            transient.append(name)
    return transient
