from typing import Any, Literal

from pydantic import BaseModel, Field


class IdeaRequest(BaseModel):
    idea: str = Field(..., min_length=2, max_length=500)
    target_customer: str = Field(default="", max_length=300)
    region: str = Field(default="한국", max_length=100)
    service_type: str = Field(default="모바일 앱", max_length=100)
    max_results_per_source: int = Field(default=3, ge=1, le=10)
    use_live_collectors: bool = True


class GeneratedQueries(BaseModel):
    customer_problem: list[str] = Field(default_factory=list)
    market: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    pricing: list[str] = Field(default_factory=list)
    implementation: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    pest: list[str] = Field(default_factory=list)


class SourceItem(BaseModel):
    source_id: str = ""
    source_type: str
    category: str
    title: str
    url: str
    snippet: str = ""
    query: str = ""
    published_at: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ReportSection(BaseModel):
    summary: str
    evidence: list[str] = Field(default_factory=list)
    unverified: list[str] = Field(default_factory=list)


class CompetitorItem(BaseModel):
    app_name: str
    url: str
    category: str | None = None
    rating: float | None = None
    review_count: int | None = None
    price: str | None = None
    source_id: str


class CompetitorsSection(BaseModel):
    items: list[CompetitorItem] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    unverified: list[str] = Field(default_factory=list)


class ImplementationSection(BaseModel):
    apis: list[str] = Field(default_factory=list)
    technical_constraints: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    unverified: list[str] = Field(default_factory=list)


class PestSubsection(BaseModel):
    summary: str
    signals: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    unverified: list[str] = Field(default_factory=list)


class PestSection(BaseModel):
    political: PestSubsection
    economic: PestSubsection
    social: PestSubsection
    technological: PestSubsection


class ReportBody(BaseModel):
    customer_problem: ReportSection
    market_signals: ReportSection
    competitors: CompetitorsSection
    pricing: ReportSection
    implementation: ImplementationSection
    pest: PestSection
    unknowns: list[str] = Field(default_factory=list)


class ReportMeta(BaseModel):
    confidence_level: Literal["High", "Medium", "Low"]
    confidence_reasons: list[str] = Field(default_factory=list)
    llm_used: bool = False
    live_collectors_used: bool = False
    skipped_collectors: list[str] = Field(default_factory=list)
    failed_collectors: list[str] = Field(default_factory=list)
    collector_errors: dict[str, str] = Field(default_factory=dict)


class ReportResponse(BaseModel):
    input: IdeaRequest
    generated_queries: GeneratedQueries
    report: ReportBody
    sources: list[SourceItem] = Field(default_factory=list)
    meta: ReportMeta
