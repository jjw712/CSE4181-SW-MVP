from app.schemas.report import SourceItem


def normalize_sources(sources: list[SourceItem]) -> list[SourceItem]:
    normalized: list[SourceItem] = []
    counters: dict[str, int] = {}
    seen_keys: set[str] = set()

    for source in sources:
        if not source.url:
            continue

        dedupe_key = f"{source.source_type}|{source.url}|{source.title}|{source.query}"
        if dedupe_key in seen_keys:
            continue

        seen_keys.add(dedupe_key)
        counters[source.source_type] = counters.get(source.source_type, 0) + 1
        source_id = f"{source.source_type}_{counters[source.source_type]}"

        normalized.append(source.model_copy(update={"source_id": source_id}))

    return normalized
