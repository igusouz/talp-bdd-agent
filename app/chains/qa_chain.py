"""LangChain workflow for BDD QA analysis."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import Settings, get_settings
from app.schemas.qa import QAAnalysisResponse, QARequest

logger = logging.getLogger(__name__)
PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def _load_prompt(name: str) -> str:
    """Load a prompt file from the prompts directory."""

    return (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()


def _format_acceptance_criteria(criteria: list[str]) -> str:
    """Convert criteria into a compact prompt-friendly block."""

    if not criteria:
        return "No acceptance criteria provided."

    return "\n".join(f"- {item}" for item in criteria)


class QAAnalysisChain:
    """Encapsulates the structured analysis workflow."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{system_prompt}"),
                (
                    "human",
                    "Story:\n{story}\n\nAcceptance criteria:\n{acceptance_criteria}",
                ),
            ]
        )
        self._llm = ChatOpenAI(
            model=self.settings.llm_model,
            base_url=self.settings.llm_base_url,
            api_key=self.settings.llm_api_key,
            temperature=self.settings.llm_temperature,
            timeout=self.settings.llm_timeout_seconds,
        )
        self._chain = self._prompt | self._llm.with_structured_output(QAAnalysisResponse)

    def invoke(self, request: QARequest) -> QAAnalysisResponse:
        """Run the QA analysis workflow for one user story."""

        logger.info("Running QA analysis for story length=%s", len(request.story))
        payload = {
            "system_prompt": f"{_load_prompt('system.md')}\n\n{_load_prompt('few_shots.md')}",
            "story": request.story.strip(),
            "acceptance_criteria": _format_acceptance_criteria(request.acceptance_criteria),
        }
        return self._chain.invoke(payload)


@lru_cache(maxsize=1)
def get_qa_chain() -> QAAnalysisChain:
    """Return a cached chain instance for reuse across requests."""

    return QAAnalysisChain()
