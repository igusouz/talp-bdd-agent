"""Pydantic schemas for the BDD QA workflow."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class QARequest(BaseModel):
    """Incoming payload for story analysis."""

    story: str = Field(min_length=1, description="User story to analyze.")
    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="Optional acceptance criteria associated with the story.",
    )


class BDDScenario(BaseModel):
    """Structured BDD scenario returned by the agent."""

    title: str = Field(description="Short scenario title.")
    scenario_type: Literal["positive", "negative", "edge"] = Field(
        description="Scenario classification for test planning.",
    )
    gherkin: str = Field(description="Scenario written in Gherkin syntax.")
    notes: list[str] = Field(default_factory=list, description="Useful implementation or validation notes.")


class QAAnalysisResponse(BaseModel):
    """Structured response returned by the QA analysis chain."""

    summary: str = Field(description="Concise analysis summary.")
    bdd_scenarios: list[BDDScenario] = Field(default_factory=list)
    negative_cases: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    automation_suggestions: list[str] = Field(default_factory=list)
    questions_for_refinement: list[str] = Field(default_factory=list)
