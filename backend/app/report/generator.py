from app.schemas.report import (
    CompetitorItem,
    CompetitorsSection,
    ImplementationSection,
    PestSection,
    PestSubsection,
    ReportBody,
    ReportSection,
    SourceItem,
)


def generate_report_body(sources: list[SourceItem]) -> ReportBody:
    grouped = _group_by_category(sources)
    competitors = _competitor_items(grouped.get("competitors", []))

    return ReportBody(
        customer_problem=_basic_section(
            grouped.get("customer_problem", []),
            found_summary="고객 문제와 관련된 출처 기반 문서가 확인되었습니다.",
            missing_summary="고객 문제를 직접 뒷받침하는 출처가 아직 부족합니다.",
            missing_hint="사용자 인터뷰, 커뮤니티 글, 리뷰 데이터 등 고객 문제 근거가 더 필요합니다.",
        ),
        market_signals=_basic_section(
            grouped.get("market", []),
            found_summary="시장/수요 관련 신호가 일부 확인되었습니다.",
            missing_summary="시장/수요 관련 신호가 충분히 수집되지 않았습니다.",
            missing_hint="Naver DataLab, 뉴스, 트렌드 데이터 보강이 필요합니다.",
        ),
        competitors=CompetitorsSection(
            items=competitors,
            evidence=[item.source_id for item in competitors],
            unverified=[] if competitors else ["경쟁 앱 후보가 충분히 확인되지 않았습니다."],
        ),
        pricing=_basic_section(
            grouped.get("pricing", []) + grouped.get("competitors", []),
            found_summary="경쟁 앱 또는 유사 서비스에서 가격/수익화 단서를 확인했습니다.",
            missing_summary="가격/수익화 구조를 판단할 근거가 아직 부족합니다.",
            missing_hint="App Store 가격, 구독 여부, 경쟁 서비스 pricing page 확인이 필요합니다.",
        ),
        implementation=_implementation_section(grouped),
        pest=PestSection(
            political=_pest_section(
                grouped.get("pest_political", []),
                "Political",
                "정책/규제 관련 신호가 일부 확인되었습니다.",
            ),
            economic=_pest_section(
                grouped.get("pest_economic", []),
                "Economic",
                "시장/경제 관련 뉴스 신호가 일부 확인되었습니다.",
            ),
            social=_pest_section(
                grouped.get("pest_social", []),
                "Social",
                "사용자 행동 또는 커뮤니티 반응 신호가 일부 확인되었습니다.",
            ),
            technological=_pest_section(
                grouped.get("pest_technological", []),
                "Technological",
                "기술 생태계 또는 구현 자료 신호가 일부 확인되었습니다.",
            ),
        ),
        unknowns=_unknowns(grouped, competitors),
    )


def _group_by_category(sources: list[SourceItem]) -> dict[str, list[SourceItem]]:
    grouped: dict[str, list[SourceItem]] = {}
    for source in sources:
        grouped.setdefault(source.category, []).append(source)
    return grouped


def _basic_section(
    sources: list[SourceItem],
    found_summary: str,
    missing_summary: str,
    missing_hint: str,
) -> ReportSection:
    if sources:
        return ReportSection(
            summary=f"{found_summary} 총 {len(sources)}개 source가 연결되었습니다.",
            evidence=[source.source_id for source in sources[:5]],
        )

    return ReportSection(
        summary=missing_summary,
        unverified=[missing_hint],
    )


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


def _implementation_section(grouped: dict[str, list[SourceItem]]) -> ImplementationSection:
    sources = grouped.get("implementation", []) + grouped.get("pest_technological", [])
    apis = [source.title for source in sources if "api" in f"{source.title} {source.snippet}".lower()]
    constraints = []

    if not sources:
        constraints.append("구현/API 관련 출처가 부족하여 기술 난이도를 강하게 판단하기 어렵습니다.")
    if grouped.get("competitors"):
        constraints.append("경쟁 앱 feature를 직접 분석하려면 상세 페이지와 리뷰 데이터가 추가로 필요합니다.")

    return ImplementationSection(
        apis=apis[:5],
        technical_constraints=constraints,
        evidence=[source.source_id for source in sources[:5]],
        unverified=[] if sources else ["GitHub, 공식 API 문서, 기술 블로그 보강이 필요합니다."],
    )


def _pest_section(sources: list[SourceItem], label: str, found_summary: str) -> PestSubsection:
    if sources:
        return PestSubsection(
            summary=f"{found_summary} 총 {len(sources)}개 source가 연결되었습니다.",
            signals=[source.title for source in sources[:3]],
            evidence=[source.source_id for source in sources[:5]],
        )

    return PestSubsection(
        summary=f"{label} 신호를 판단할 출처가 아직 부족합니다.",
        unverified=[f"{label} 관점의 뉴스, 커뮤니티, 기술 자료 보강이 필요합니다."],
    )


def _unknowns(grouped: dict[str, list[SourceItem]], competitors: list[CompetitorItem]) -> list[str]:
    unknowns: list[str] = []
    if not grouped.get("customer_problem"):
        unknowns.append("실제 사용자 불만과 pain point는 아직 직접 검증되지 않았습니다.")
    if not grouped.get("market"):
        unknowns.append("검색 관심도와 시장 수요는 아직 충분히 확인되지 않았습니다.")
    if not competitors:
        unknowns.append("경쟁 앱 후보가 부족하여 차별화 판단이 제한적입니다.")
    if not grouped.get("pricing") and not competitors:
        unknowns.append("가격/수익화 구조는 추가 조사가 필요합니다.")
    return unknowns
