"""Service layer for QA analysis requests."""

from __future__ import annotations

import logging

from app.chains.qa_chain import QAAnalysisChain, get_qa_chain
from app.schemas.qa import QAAnalysisResponse, QARequest

logger = logging.getLogger(__name__)


class QAService:
    """Coordinates incoming requests with the LangChain workflow."""

    def __init__(self, chain: QAAnalysisChain | None = None) -> None:
        self._chain = chain or get_qa_chain()

    def analyze(self, request: QARequest) -> QAAnalysisResponse:
        """Analyze a user story and return a structured QA response."""

        logger.debug("Received QA request with %s acceptance criteria", len(request.acceptance_criteria))
        return self._chain.invoke(request)


def get_qa_service() -> QAService:
    """FastAPI dependency that returns the shared QA service."""

    return QAService()
