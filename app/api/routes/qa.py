"""API routes for QA analysis."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas.qa import QAAnalysisResponse, QARequest
from app.services.qa_service import QAService, get_qa_service

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/analyze", response_model=QAAnalysisResponse)
def analyze_story(
    payload: QARequest,
    service: QAService = Depends(get_qa_service),
) -> QAAnalysisResponse:
    """Analyze a story and return structured QA guidance."""

    return service.analyze(payload)
