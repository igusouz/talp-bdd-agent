"""LangChain workflow for BDD QA analysis."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import Settings, get_settings
from app.prompts.repository import PromptBundle, get_prompt_repository
from app.schemas.qa import QAAnalysisResponse, QARequest

logger = logging.getLogger(__name__)
PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
PROMPT_REPOSITORY = get_prompt_repository()


def _load_prompt(name: str) -> str:
    """Load a prompt file from the prompts directory.

    This preserves a small compatibility helper for tests while the
    implementation uses the structured prompt repository internally.
    """

    legacy_candidates = {
        "system.md": [PROMPTS_DIR / "system" / "qa.md", PROMPTS_DIR / "system.md"],
        "few_shots.md": [PROMPTS_DIR / "few_shots" / "qa.md", PROMPTS_DIR / "few_shots.md"],
    }
    candidates = legacy_candidates.get(name, [PROMPTS_DIR / name])

    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8").strip()

    raise FileNotFoundError(f"Prompt file not found: {name}")


def _format_acceptance_criteria(criteria: list[str]) -> str:
    """Convert criteria into a compact prompt-friendly block."""

    if not criteria:
        return "No acceptance criteria provided."

    return "\n".join(f"- {item}" for item in criteria)


class QAAnalysisChain:
    """Encapsulates the structured analysis workflow."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._prompts: PromptBundle = PROMPT_REPOSITORY.load_bundle("qa")
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{system_prompt}"),
                (
                    "human",
                    "{human_prompt}",
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

        logger.info(
            "Running QA analysis using prompt_version=%s story_length=%s",
            self._prompts.version,
            len(request.story),
        )
        payload = {
            "system_prompt": self._prompts.compose_system_prompt(),
            "human_prompt": self._prompts.render_human_prompt(
                story=request.story.strip(),
                acceptance_criteria=_format_acceptance_criteria(request.acceptance_criteria),
            ),
            "story": request.story.strip(),
        }
        try:
            return self._chain.invoke(payload)
        except Exception:
            logger.exception("QA analysis failed for prompt_version=%s", self._prompts.version)
            raise


@lru_cache(maxsize=1)
def get_qa_chain() -> QAAnalysisChain:
    """Return a cached chain instance for reuse across requests."""

    return QAAnalysisChain()
