from app.schemas.report import (
    CompetitorItem,
    CompetitorsSection,
    GeneratedQueries,
    IdeaRequest,
    ImplementationSection,
    KeywordSection,
    ReportBody,
    ReportSection,
    SourceItem,
)


DIFFICULTY_RULES = {
    "login": "로그인/회원 기능은 MVP에서는 선택 기능으로 두고, 저장 리포트가 필요할 때 도입합니다.",
    "push": "push notification은 외부 서비스 연동과 사용자 동의 처리가 필요해 초기 MVP에서는 제외하거나 후순위로 둡니다.",
    "chat": "real-time chat은 구현 난이도와 운영 부담이 크므로 검증 MVP 범위에서는 제외하는 것이 안전합니다.",
    "payment": "payment는 정책, 정산, 보안 고려가 필요하므로 유료화 검증 전까지는 mock 또는 수동 결제로 대체합니다.",
    "calendar": "calendar integration은 외부 API 권한과 동기화 이슈가 있어 핵심 가치 검증 이후에 도입합니다.",
    "ai": "AI 기능은 비용과 품질 변동성이 있으므로 rule 기반 기능과 함께 제한된 범위로 검증합니다.",
}


def generate_report_body(
    payload: IdeaRequest,
    queries: GeneratedQueries,
    sources: list[SourceItem],
) -> ReportBody:
    grouped = _group_by_category(sources)
    competitors = _competitor_items(grouped.get("competitors", []))
    unknowns = _unknowns(grouped, competitors)

    return ReportBody(
        idea_summary=_idea_summary_section(payload),
        target_users=_target_users_section(payload),
        related_keywords=_related_keywords_section(queries),
        search_demand=_search_demand_section(grouped),
        competitors=CompetitorsSection(
            items=competitors,
            evidence=[item.source_id for item in competitors],
            unverified=[] if competitors else ["Apple iTunes Search API에서 경쟁 앱 후보가 충분히 확인되지 않았습니다."],
        ),
        review_pain_points=_review_pain_points_section(grouped),
        monetization=_monetization_section(grouped, competitors),
        mvp_scope=_mvp_scope_section(payload, grouped),
        risks=_risks_section(grouped, competitors),
        recommendation=_recommendation_section(grouped, competitors),
        data_confidence=_data_confidence_section(sources, unknowns),
        unknowns=unknowns,
    )


def _group_by_category(sources: list[SourceItem]) -> dict[str, list[SourceItem]]:
    grouped: dict[str, list[SourceItem]] = {}
    for source in sources:
        grouped.setdefault(source.category, []).append(source)
    return grouped


def _idea_summary_section(payload: IdeaRequest) -> ReportSection:
    target = payload.target_customer or "정의되지 않은 사용자"
    summary = (
        f"'{payload.idea}'는 {target}을 대상으로 한 {payload.service_type} 아이디어입니다. "
        "현재 리포트는 성공 가능성을 예측하지 않고, 수집 가능한 검색/시장/경쟁 신호를 기준으로 검증 포인트를 정리합니다."
    )
    return ReportSection(summary=summary)


def _target_users_section(payload: IdeaRequest) -> ReportSection:
    if payload.target_customer:
        return ReportSection(
            summary=f"입력 기준 주요 타깃은 {payload.target_customer}입니다. 실제 구매자, 반복 사용자, 초기 인터뷰 대상은 별도로 검증해야 합니다.",
            unverified=["타깃 사용자의 실제 pain point와 지불 의사는 아직 직접 검증되지 않았습니다."],
        )
    return ReportSection(
        summary="타깃 사용자가 구체적으로 입력되지 않았습니다.",
        unverified=["초기 MVP 전 사용자군, 사용 상황, 반복 사용 빈도를 먼저 정의해야 합니다."],
    )


def _related_keywords_section(queries: GeneratedQueries) -> KeywordSection:
    keywords = _dedupe(
        [
            *queries.customer_problem,
            *queries.market,
            *queries.competitors,
            *queries.pricing,
            *queries.implementation,
            *queries.alternatives,
            *queries.pest,
        ],
        limit=18,
    )
    return KeywordSection(
        summary="사용자 입력과 Gemini/query rule을 바탕으로 수집에 사용할 관련 키워드를 생성했습니다.",
        keywords=keywords,
        unverified=["키워드는 검색 수집을 돕는 후보이며, 시장 수요 자체를 의미하지 않습니다."],
    )


def _search_demand_section(grouped: dict[str, list[SourceItem]]) -> ReportSection:
    market_sources = grouped.get("market", [])
    datalab_sources = [source for source in market_sources if source.source_type == "naver_datalab"]
    evidence = [source.source_id for source in market_sources[:6]]

    if datalab_sources:
        zero_count = sum(1 for source in datalab_sources if source.raw.get("average_ratio") == 0)
        if zero_count == len(datalab_sources):
            summary = (
                "Naver DataLab 기준 직접 키워드의 최근 상대 관심도는 낮거나 충분히 잡히지 않았습니다. "
                "이는 절대 검색량 0을 의미하지 않으며, 키워드 표현을 넓혀 재검증할 필요가 있습니다."
            )
        else:
            summary = "Naver DataLab과 뉴스/문서 source에서 일부 검색 수요 및 시장 맥락 신호가 확인되었습니다."
        return ReportSection(
            summary=summary,
            evidence=evidence,
            unverified=["Naver DataLab은 상대 지표이므로 절대 검색량이나 시장 규모로 해석하면 안 됩니다."],
        )

    if market_sources:
        return ReportSection(
            summary="뉴스/문서 기반 시장 맥락은 일부 확인되었지만 검색 트렌드 source는 충분하지 않습니다.",
            evidence=evidence,
            unverified=["Naver DataLab 또는 Google Trends 같은 trend source 보강이 필요합니다."],
        )

    return ReportSection(
        summary="검색 수요를 판단할 수 있는 trend/source가 부족합니다.",
        unverified=["Naver DataLab, Naver Search, Google Trends 등 검색 관심도 source 보강이 필요합니다."],
    )


def _review_pain_points_section(grouped: dict[str, list[SourceItem]]) -> ReportSection:
    review_sources = grouped.get("reviews", [])
    customer_sources = grouped.get("customer_problem", [])
    if review_sources:
        return ReportSection(
            summary="리뷰 source에서 사용자 불만 후보가 일부 확인되었습니다.",
            evidence=[source.source_id for source in review_sources[:5]],
        )

    if customer_sources:
        return ReportSection(
            summary="웹 문서에서 사용자 문제와 관련된 단서는 일부 확인되지만, 실제 app review 기반 불만 분석은 아직 구현 범위에 포함되지 않았습니다.",
            evidence=[source.source_id for source in customer_sources[:5]],
            unverified=["Apple/Google Play review text 수집과 complaint clustering은 현재 MVP의 후속 확장 항목입니다."],
        )

    return ReportSection(
        summary="리뷰 기반 사용자 불만을 판단할 데이터가 아직 없습니다.",
        unverified=["리뷰 수집 API 또는 third-party review collector가 필요합니다."],
    )


def _monetization_section(
    grouped: dict[str, list[SourceItem]],
    competitors: list[CompetitorItem],
) -> ReportSection:
    evidence = [item.source_id for item in competitors[:5]]
    if competitors:
        prices = _dedupe([item.price or "Unknown" for item in competitors], limit=5)
        summary = (
            "Apple iTunes Search API에서 확인된 경쟁 앱 metadata 기준 가격/수익화 단서는 "
            f"{', '.join(prices)}입니다. 구독, 인앱결제, 실제 매출은 별도 확인이 필요합니다."
        )
        return ReportSection(
            summary=summary,
            evidence=evidence,
            unverified=["App Store 검색 결과만으로 수익성이나 구매 전환을 판단할 수 없습니다."],
        )

    pricing_sources = grouped.get("pricing", [])
    if pricing_sources:
        return ReportSection(
            summary="가격/수익화 관련 문서 신호가 일부 확인되었습니다.",
            evidence=[source.source_id for source in pricing_sources[:5]],
            unverified=["경쟁 앱의 실제 결제 구조와 구독 여부는 추가 확인이 필요합니다."],
        )

    return ReportSection(
        summary="수익화 구조를 판단할 경쟁 앱 가격 또는 pricing source가 부족합니다.",
        unverified=["경쟁 앱의 가격, 인앱결제, 구독 여부, freemium 사례를 추가로 확인해야 합니다."],
    )


def _mvp_scope_section(payload: IdeaRequest, grouped: dict[str, list[SourceItem]]) -> ImplementationSection:
    idea_text = f"{payload.idea} {payload.service_type}".lower()
    constraints = [
        rule
        for keyword, rule in DIFFICULTY_RULES.items()
        if keyword in idea_text or _korean_keyword_match(keyword, idea_text)
    ]
    if grouped.get("competitors"):
        constraints.append("경쟁 앱 feature를 직접 비교하려면 상세 페이지와 리뷰 데이터가 추가로 필요합니다.")
    if not grouped.get("pest_technological") and not grouped.get("implementation"):
        constraints.append("구현/API 관련 source가 부족하여 기술 난이도 판단은 보수적으로 유지합니다.")

    return ImplementationSection(
        summary="1인 MVP는 핵심 입력, 간단한 저장/조회, 기본 알림 또는 리포트 출력처럼 작은 기능 단위로 제한하는 것이 적절합니다.",
        mvp_features=[
            "아이디어 또는 문제 상황 입력",
            "핵심 키워드 자동 생성",
            "검색/경쟁 앱 source 수집",
            "표준 리포트 출력",
            "데이터 신뢰도와 미확인 항목 표시",
        ],
        apis=[source.title for source in grouped.get("pest_technological", [])[:5]],
        technical_constraints=constraints,
        evidence=[source.source_id for source in grouped.get("pest_technological", [])[:5]],
        unverified=[] if grouped.get("pest_technological") else ["공식 API 문서, GitHub, 기술 블로그 기반 구현 자료 보강이 필요합니다."],
    )


def _risks_section(grouped: dict[str, list[SourceItem]], competitors: list[CompetitorItem]) -> ReportSection:
    risks: list[str] = []
    evidence: list[str] = []

    if not grouped.get("customer_problem"):
        risks.append("사용자 불만 source가 부족해 문제 강도를 판단하기 어렵습니다.")
    else:
        evidence.extend(source.source_id for source in grouped["customer_problem"][:3])

    datalab_sources = [source for source in grouped.get("market", []) if source.source_type == "naver_datalab"]
    if datalab_sources and all(source.raw.get("average_ratio") == 0 for source in datalab_sources):
        risks.append("직접 키워드의 DataLab 상대 관심도가 낮아 키워드 확장 또는 pivot 검토가 필요합니다.")
        evidence.extend(source.source_id for source in datalab_sources[:3])

    if not competitors:
        risks.append("경쟁 앱 후보가 부족해 차별화와 수익화 비교가 제한됩니다.")
    else:
        evidence.extend(item.source_id for item in competitors[:3])

    if not grouped.get("reviews"):
        risks.append("리뷰 기반 사용자 불만 데이터가 없어 실제 불편을 정량/정성으로 확인하지 못했습니다.")

    if not risks:
        risks.append("수집 데이터는 일부 확보되었지만, 현재 결과는 앱 성공 가능성 판단이 아니라 추가 검증 방향 제시에 가깝습니다.")

    return ReportSection(summary=" ".join(risks), evidence=_dedupe(evidence, limit=8))


def _recommendation_section(
    grouped: dict[str, list[SourceItem]],
    competitors: list[CompetitorItem],
) -> ReportSection:
    datalab_sources = [source for source in grouped.get("market", []) if source.source_type == "naver_datalab"]
    has_low_search = bool(datalab_sources) and all(source.raw.get("average_ratio") == 0 for source in datalab_sources)
    has_competitors = bool(competitors)
    has_customer_sources = bool(grouped.get("customer_problem"))

    if has_low_search and not has_customer_sources:
        summary = "바로 개발하기보다 키워드 범위를 넓히고 사용자 인터뷰 또는 커뮤니티 조사를 먼저 진행하는 방향을 추천합니다."
    elif has_competitors and has_low_search:
        summary = "유사 앱 후보는 있으나 직접 검색 관심도는 낮게 잡히므로, 기능 범위를 줄인 MVP로 문제 강도부터 검증하는 방향을 추천합니다."
    elif has_competitors and has_customer_sources:
        summary = "경쟁 앱과 사용자 문제 단서가 있으므로, 차별화 기능 1~2개만 선택한 작은 MVP로 검증을 시작할 수 있습니다."
    else:
        summary = "현재 데이터만으로 개발 착수 판단은 이르며, 추가 source 수집 후 start/pivot/scope-down 여부를 다시 결정하는 것이 좋습니다."

    return ReportSection(
        summary=summary,
        unverified=["추천 방향은 수집 source 기반의 의사결정 보조이며 성공 예측이 아닙니다."],
    )


def _data_confidence_section(sources: list[SourceItem], unknowns: list[str]) -> ReportSection:
    source_types = {source.source_type for source in sources}
    categories = {source.category for source in sources}
    summary = (
        f"현재 리포트는 source {len(sources)}개, source type {len(source_types)}종, "
        f"category {len(categories)}종을 기반으로 합니다. "
        "confidence는 데이터 커버리지, source 신뢰도, 최신성, 신호 간 일치 여부를 기준으로 해석해야 합니다."
    )
    unverified = unknowns[:6] or ["추가 미확인 항목은 현재 rule 기준에서 감지되지 않았습니다."]
    return ReportSection(summary=summary, evidence=[source.source_id for source in sources[:8]], unverified=unverified)


def _competitor_items(sources: list[SourceItem]) -> list[CompetitorItem]:
    items: list[CompetitorItem] = []
    for source in sources:
        raw = source.raw
        items.append(
            CompetitorItem(
                app_name=raw.get("app_name") or source.title,
                url=source.url,
                category=raw.get("category"),
                rating=raw.get("rating"),
                review_count=raw.get("review_count"),
                price=raw.get("price"),
                source_id=source.source_id,
            )
        )
    return items


def _unknowns(grouped: dict[str, list[SourceItem]], competitors: list[CompetitorItem]) -> list[str]:
    unknowns: list[str] = []
    if not grouped.get("customer_problem"):
        unknowns.append("실제 사용자 불만과 pain point는 아직 직접 검증되지 않았습니다.")
    if not grouped.get("market"):
        unknowns.append("검색 관심도와 시장 수요는 아직 충분히 확인되지 않았습니다.")
    if not competitors:
        unknowns.append("경쟁 앱 후보가 부족하여 차별화 판단이 제한적입니다.")
    if not grouped.get("reviews"):
        unknowns.append("리뷰 기반 사용자 불만 분석은 현재 MVP에서 직접 수집되지 않았습니다.")
    if not grouped.get("pest_technological") and not grouped.get("implementation"):
        unknowns.append("구현/API 관련 source가 부족하여 기술 난이도 판단은 제한적입니다.")
    if not grouped.get("pricing") and not competitors:
        unknowns.append("가격/수익화 구조는 추가 조사가 필요합니다.")
    unknowns.append("Google Play 경쟁 앱 데이터는 공식 competitor search API 제약으로 현재 MVP에서 제한적으로만 다룹니다.")
    return _dedupe(unknowns, limit=8)


def _dedupe(values: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = " ".join(str(value).split())
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def _korean_keyword_match(keyword: str, text: str) -> bool:
    mapping = {
        "login": ["로그인", "회원"],
        "push": ["푸시", "알림"],
        "chat": ["채팅", "메신저"],
        "payment": ["결제", "구독"],
        "calendar": ["캘린더", "일정"],
        "ai": ["ai", "인공지능", "식재료 인식"],
    }
    return any(term in text for term in mapping.get(keyword, []))
