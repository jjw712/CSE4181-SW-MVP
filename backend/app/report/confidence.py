from app.schemas.report import ReportMeta, SourceItem


def calculate_confidence(
    sources: list[SourceItem],
    skipped_collectors: list[str],
    failed_collectors: list[str],
    collector_errors: dict[str, str],
    llm_used: bool,
    live_collectors_used: bool,
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
        reasons.append(f"실패한 collector: {', '.join(failed_collectors)}")
    if skipped_collectors:
        reasons.append(f"건너뛴 collector: {', '.join(skipped_collectors)}")

    if source_count >= 8 and len(source_types) >= 4 and not failed_collectors:
        level = "High"
    elif source_count >= 3 and len(source_types) >= 2:
        level = "Medium"
    else:
        level = "Low"

    return ReportMeta(
        confidence_level=level,
        confidence_reasons=reasons,
        llm_used=llm_used,
        live_collectors_used=live_collectors_used,
        skipped_collectors=skipped_collectors,
        failed_collectors=failed_collectors,
        collector_errors=collector_errors,
    )
