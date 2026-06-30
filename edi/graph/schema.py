"""
schema.py — Node and edge dataclass definitions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ProblemNode:
    slug: str
    label: str
    recurrence_count: int = 0
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    temporal_trend: list[dict] = field(default_factory=list)
    dominant_outcome: str = "unknown"
    top_lesson: str | None = None
    repos_seen_in: list[str] = field(default_factory=list)

@dataclass
class DecisionNode:
    id: str
    thread_id: str
    problem_slug: str
    repo: str
    choice: str
    outcome_type: str
    outcome_description: str | None
    lesson: str | None
    is_regret: bool
    regret_alternative: str | None
    extraction_confidence: float
    evidence_confidence: float
    overall_confidence: float
    confidence_reason: str
    uncertainties: list[str]
    evidence_url: str
    team_size: str
    project_stage: str
    technology_stack: list[str]
    community_size: int
    year: int
    created_at: datetime

    def to_cognee_text(self) -> str:
        parts = [
            f"PROBLEM: {self.problem_slug}",
            f"REPOSITORY: {self.repo}",
            f"DECISION: {self.choice or 'unspecified'}",
            f"OUTCOME: {self.outcome_type} — {self.outcome_description or ''}",
            f"LESSON: {self.lesson or 'none recorded'}",
            f"IS_REGRET: {self.is_regret}",
            f"REGRET_ALTERNATIVE: {self.regret_alternative or 'N/A'}",
            f"CONFIDENCE: {self.overall_confidence:.2f} ({self.confidence_reason})",
            f"CONTEXT: team={self.team_size}, stage={self.project_stage}, community={self.community_size} stars",
            f"TECH_STACK: {', '.join(self.technology_stack) or 'unspecified'}",
            f"YEAR: {self.year}",
            f"EVIDENCE_URL: {self.evidence_url}",
        ]
        if self.uncertainties:
            parts.append(f"UNCERTAINTIES: {'; '.join(self.uncertainties)}")
        return "\n".join(parts)
