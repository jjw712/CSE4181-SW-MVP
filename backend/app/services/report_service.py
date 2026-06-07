from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.collectors.apple_itunes import collect_apple_itunes
from app.collectors.gdelt import collect_gdelt
from app.collectors.github import collect_github_repositories
from app.collectors.hacker_news import collect_hacker_news
from app.collectors.naver import collect_naver_datalab, collect_naver_search
from app.core.config import Settings
from app.report.confidence import calculate_confidence
from app.report.generator import generate_report_body
from app.schemas.report import GeneratedQueries, IdeaRequest, ReportResponse, SourceItem
from app.services.llm import (
    expand_queries_with_gemini,
    is_llm_configured,
    summarize_report_with_gemini,
)
from app.services.query_generator import generate_queries
from app.services.source_quality import annotate_source_relevance
from app.services.source_normalizer import normalize_sources


CollectorTask = tuple[str, Callable[[], list[SourceItem]]]


def build_report(payload: IdeaRequest, settings: Settings) -> ReportResponse:
    queries = generate_queries(payload)
    raw_sources: list[SourceItem] = []
    skipped_collectors: list[str] = []
    collector_errors: dict[str, str] = {}
    llm_configured = is_llm_configured(settings)
    llm_used = False
    llm_errors: list[str] = []

    if llm_configured and payload.use_live_collectors:
        queries, query_llm_used, query_llm_error = expand_queries_with_gemini(
            payload,
            queries,
            settings,
        )
        llm_used = llm_used or query_llm_used
        if query_llm_error:
            llm_errors.append(f"query_expansion: {query_llm_error}")

    if payload.use_live_collectors:
        tasks = _public_collector_tasks(payload, queries, settings)
        if settings.naver_client_id and settings.naver_client_secret:
            tasks.extend(_naver_collector_tasks(payload, queries, settings))
        else:
            skipped_collectors.extend(["naver_search", "naver_news", "naver_datalab"])

        raw_sources, collector_errors = _run_collectors_parallel(tasks)
    else:
        skipped_collectors.append("live_collectors_disabled")

    if not llm_configured:
        skipped_collectors.append("llm")

    failed_collectors = list(collector_errors)
    sources = annotate_source_relevance(payload, normalize_sources(raw_sources))
    fallback_report = generate_report_body(payload, queries, sources)
    report = fallback_report

    if llm_configured:
        report, summary_llm_used, summary_llm_error = summarize_report_with_gemini(
            payload,
            queries,
            sources,
            fallback_report,
            settings,
        )
        llm_used = llm_used or summary_llm_used
        if summary_llm_error:
            llm_errors.append(f"summary: {summary_llm_error}")

    if llm_configured and not llm_used and llm_errors:
        skipped_collectors.append("llm_failed")

    meta = calculate_confidence(
        sources=sources,
        skipped_collectors=skipped_collectors,
        failed_collectors=failed_collectors,
        collector_errors=collector_errors,
        llm_used=llm_used,
        live_collectors_used=payload.use_live_collectors,
        llm_provider=settings.llm_provider if llm_configured else None,
        llm_model=settings.gemini_model if llm_configured else None,
        llm_error="; ".join(llm_errors) if llm_errors else None,
    )

    return ReportResponse(
        input=payload,
        generated_queries=queries,
        report=report,
        sources=sources,
        meta=meta,
    )


def _public_collector_tasks(
    payload: IdeaRequest,
    queries: GeneratedQueries,
    settings: Settings,
) -> list[CollectorTask]:
    return [
        (
            "apple_itunes",
            lambda: collect_apple_itunes(
                queries.competitors[0],
                payload.region,
                payload.max_results_per_source,
            ),
        ),
        (
            "hacker_news",
            lambda: collect_hacker_news(
                queries.market[0],
                payload.max_results_per_source,
                category="pest_social",
            ),
        ),
        (
            "github",
            lambda: collect_github_repositories(
                queries.implementation[0],
                payload.max_results_per_source,
                token=settings.github_token,
            ),
        ),
        (
            "gdelt",
            lambda: collect_gdelt(
                queries.pest[1],
                payload.max_results_per_source,
                category="pest_economic",
            ),
        ),
    ]


def _naver_collector_tasks(
    payload: IdeaRequest,
    queries: GeneratedQueries,
    settings: Settings,
) -> list[CollectorTask]:
    assert settings.naver_client_id is not None
    assert settings.naver_client_secret is not None

    client_id = settings.naver_client_id
    client_secret = settings.naver_client_secret
    limit = payload.max_results_per_source

    return [
        (
            "naver_search",
            lambda: collect_naver_search(
                queries.customer_problem[0],
                "customer_problem",
                "webkr",
                client_id,
                client_secret,
                limit,
            ),
        ),
        (
            "naver_news",
            lambda: collect_naver_search(
                queries.market[0],
                "market",
                "news",
                client_id,
                client_secret,
                limit,
            ),
        ),
        (
            "naver_datalab",
            lambda: collect_naver_datalab(
                queries.market,
                client_id,
                client_secret,
            ),
        ),
    ]


def _run_collectors_parallel(tasks: list[CollectorTask]) -> tuple[list[SourceItem], dict[str, str]]:
    if not tasks:
        return [], {}

    sources: list[SourceItem] = []
    errors: dict[str, str] = {}
    max_workers = min(6, len(tasks))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_name = {executor.submit(task): name for name, task in tasks}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                sources.extend(future.result())
            except Exception as error:
                errors[name] = _safe_error_message(error)

    return sources, errors


def _safe_error_message(error: Exception) -> str:
    message = f"{error.__class__.__name__}: {error}"
    return message[:240]
