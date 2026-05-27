from fastapi import APIRouter

from app.core.config import settings
from app.schemas.report import IdeaRequest, ReportResponse
from app.services.report_service import build_report

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/reports", response_model=ReportResponse)
def create_report(payload: IdeaRequest) -> ReportResponse:
    return build_report(payload, settings)
