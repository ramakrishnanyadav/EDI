"""
models.py — Pydantic request/response models.
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class IngestRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL")
    max_issues: int = Field(default=70, ge=10, le=200)
    @property
    def repo_name(self) -> str:
        return self.repo_url.rstrip("/").removeprefix("https://github.com/")

class QueryContext(BaseModel):
    team_size: Literal["small", "medium", "large"] | None = None
    project_stage: Literal["early", "growth", "mature"] | None = None
    technology: str | None = None

class QueryRequest(BaseModel):
    description: str = Field(..., min_length=10)
    context: QueryContext | None = Field(default=None)

class IngestResponse(BaseModel):
    status: str
    repo: str
    threads_fetched: int
    threads_ingested: int
    threads_skipped: int
    problems_found: int
    cached_hits: int
    message: str

class RegretCaseOut(BaseModel):
    decision: str
    regret_reason: str
    alternative: str
    evidence_url: str

class TemporalPoint(BaseModel):
    year: int
    count: int

class QueryResponse(BaseModel):
    problem_slug: str
    problem_label: str
    recurrence_count: int
    similar_cases: int
    dominant_outcome: str
    outcome_breakdown: dict[str, int]
    decisions: list[str]
    lessons: list[str]
    regret_cases: list[RegretCaseOut]
    evidence: list[str]
    temporal_trend: list[TemporalPoint]
    overall_confidence: float
    evidence_score: float = 0.0
    recurrence_score: float = 0.0
    extraction_score: float = 0.0
    inference_degraded: bool = False
    uncertainties: list[str]
    answer: str

class ProblemSummary(BaseModel):
    slug: str
    label: str
    recurrence_count: int
    dominant_outcome: str
    top_lesson: str | None
    repos: list[str]
    last_seen: int | None

class HealthResponse(BaseModel):
    status: str
    version: str
    cognee_version: str
    cache_stats: dict[str, int]
    graph_ready: bool
