import os
from pathlib import Path

BASE_DIR = Path("c:/Users/Ramakrishna/OneDrive/Pictures/java/Documents/Projects/cognee/edi")

FILES = {
    ".env": """# ── LLM ──────────────────────────────────────────────────────────────
LLM_PROVIDER=openai
LLM_MODEL=Qwen/Qwen3-VL-8B-Thinking
OPENAI_API_KEY=your_featherless_api_key
OPENAI_BASE_URL=https://api.featherless.ai/v1
LLM_TEMPERATURE=0.0

# ── Embeddings ────────────────────────────────────────────────────────
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=your_openai_embedding_key

# ── Storage (embedded, zero infra) ───────────────────────────────────
VECTOR_DB_PROVIDER=lancedb
GRAPH_DATABASE_PROVIDER=ladybug
DB_PROVIDER=sqlite

# ── GitHub ────────────────────────────────────────────────────────────
GITHUB_TOKEN=your_github_token

# ── App ──────────────────────────────────────────────────────────────
TELEMETRY_DISABLED=true
ENABLE_BACKEND_ACCESS_CONTROL=false
CACHING=false
LOG_LEVEL=WARNING
""",
    "ingestion/taxonomy.py": """\"\"\"
taxonomy.py — Canonical problem taxonomy.

The single most important file in the project.
Every extracted problem maps to one slug here or is marked unknown.
Locked — never add slugs during ingestion, only via human review.
\"\"\"
from __future__ import annotations

PROBLEM_TAXONOMY: dict[str, str] = {
    "api-design":                "API Design",
    "authentication-strategy":   "Authentication Strategy",
    "breaking-changes":          "Breaking Changes & Versioning",
    "caching-strategy":          "Caching Strategy",
    "concurrency-handling":      "Concurrency Handling",
    "configuration-management":  "Configuration Management",
    "data-modeling":             "Data Modeling",
    "database-selection":        "Database Selection",
    "dependency-management":     "Dependency Management",
    "deployment-complexity":     "Deployment Complexity",
    "memory-management":         "Memory Management",
    "monolith-vs-microservices": "Monolith vs Microservices",
    "observability":             "Observability",
    "performance-optimization":  "Performance Optimization",
    "query-performance":         "Query Performance",
    "rate-limiting":             "Rate Limiting",
    "schema-evolution":          "Schema Evolution",
    "security-model":            "Security Model",
    "state-management":          "State Management",
    "testing-strategy":          "Testing Strategy",
}

VALID_SLUGS: frozenset[str] = frozenset(PROBLEM_TAXONOMY.keys())


def is_valid_slug(slug: str) -> bool:
    return slug in VALID_SLUGS


def get_label(slug: str) -> str:
    return PROBLEM_TAXONOMY.get(slug, slug.replace("-", " ").title())


def taxonomy_for_prompt() -> str:
    lines = [f"  {i:02d}. {slug}  ({label})"
             for i, (slug, label) in enumerate(sorted(PROBLEM_TAXONOMY.items()), 1)]
    return "\\n".join(lines)
""",
    "ingestion/cache.py": """\"\"\"
cache.py — Pickle cache for extraction results.

Keyed by thread ID. Every ingestion run is restartable from any crash point.
\"\"\"
from __future__ import annotations

import hashlib
import logging
import os
import pickle
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CACHE_DIR = Path(os.getenv("CACHE_DIR", ".edi_cache"))


def _key_path(thread_id: str) -> Path:
    safe = hashlib.sha256(thread_id.encode()).hexdigest()
    return CACHE_DIR / f"{safe}.pkl"


def get(thread_id: str) -> Any | None:
    path = _key_path(thread_id)
    if not path.exists():
        return None
    try:
        with path.open("rb") as f:
            return pickle.load(f)
    except Exception as exc:
        logger.warning("Cache read failed for %s: %s", thread_id, exc)
        return None


def set(thread_id: str, value: Any) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _key_path(thread_id)
    try:
        with path.open("wb") as f:
            pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as exc:
        logger.warning("Cache write failed for %s: %s", thread_id, exc)


def exists(thread_id: str) -> bool:
    return _key_path(thread_id).exists()


def clear_all() -> int:
    if not CACHE_DIR.exists():
        return 0
    count = 0
    for p in CACHE_DIR.glob("*.pkl"):
        p.unlink(missing_ok=True)
        count += 1
    return count


def stats() -> dict[str, int]:
    if not CACHE_DIR.exists():
        return {"total": 0, "size_kb": 0}
    files = list(CACHE_DIR.glob("*.pkl"))
    size = sum(f.stat().st_size for f in files)
    return {"total": len(files), "size_kb": size // 1024}
""",
    "ingestion/github.py": """\"\"\"
github.py — GitHub data fetcher.

Fetches Issues, PRs, and Discussions from target repositories.
Respects rate limits. Returns normalized thread dicts ready for extraction.
\"\"\"
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

from github import Github, GithubException, RateLimitExceededException

logger = logging.getLogger(__name__)

DEFAULT_REPOS = [
    "topoteretes/cognee",
    "langchain-ai/langchain",
    "run-llama/llama_index",
]

@dataclass(frozen=True, slots=True)
class GitHubThread:
    id: str           # unique: "owner/repo#number/type"
    repo: str
    repo_url: str
    number: int
    title: str
    body: str
    url: str
    thread_type: str  # "issue" | "pr" | "discussion"
    created_at: datetime
    labels: list[str]
    comments_text: str
    stars: int
    forks: int
    contributors_count: int

    def full_text(self) -> str:
        parts = [f"Title: {self.title}", f"Body: {self.body or '(empty)'}"]
        if self.comments_text:
            parts.append(f"Discussion:\\n{self.comments_text}")
        return "\\n\\n".join(parts)[:6000]

def _safe_body(text: str | None) -> str:
    return (text or "").strip()[:3000]

def _fetch_comments(item, max_comments: int = 8) -> str:
    try:
        comments = list(item.get_comments())[:max_comments]
        return "\\n---\\n".join(
            f"@{c.user.login}: {_safe_body(c.body)}"
            for c in comments if c.body
        )
    except Exception:
        return ""

def _repo_meta(repo) -> dict:
    try:
        contributors = repo.get_contributors()
        count = sum(1 for _ in contributors)
    except Exception:
        count = 0
    return {
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "contributors_count": min(count, 500),
    }

def fetch_threads(
    repo_names: list[str] | None = None,
    max_per_repo: int = 70,
    token: str | None = None,
) -> list[GitHubThread]:
    token = token or os.getenv("GITHUB_TOKEN")
    if not token or token == "your_github_token":
        raise ValueError(
            "GITHUB_TOKEN not set. Add your token to .env — "
            "get one free at https://github.com/settings/tokens"
        )

    g = Github(token, per_page=100, retry=3)
    repos = repo_names or DEFAULT_REPOS
    threads: list[GitHubThread] = []

    for repo_name in repos:
        logger.info("Fetching from %s ...", repo_name)
        try:
            repo = g.get_repo(repo_name)
            meta = _repo_meta(repo)

            for issue in _paginate(repo.get_issues(state="closed", sort="comments"), max_per_repo // 2):
                if issue.pull_request:
                    continue
                thread = GitHubThread(
                    id=f"{repo_name}#{issue.number}/issue",
                    repo=repo_name,
                    repo_url=f"https://github.com/{repo_name}",
                    number=issue.number,
                    title=issue.title,
                    body=_safe_body(issue.body),
                    url=issue.html_url,
                    thread_type="issue",
                    created_at=issue.created_at,
                    labels=[l.name for l in issue.labels],
                    comments_text=_fetch_comments(issue),
                    **meta,
                )
                threads.append(thread)

            for pr in _paginate(repo.get_pulls(state="closed", sort="updated", direction="desc"), max_per_repo // 2):
                if not pr.merged:
                    continue
                thread = GitHubThread(
                    id=f"{repo_name}#{pr.number}/pr",
                    repo=repo_name,
                    repo_url=f"https://github.com/{repo_name}",
                    number=pr.number,
                    title=pr.title,
                    body=_safe_body(pr.body),
                    url=pr.html_url,
                    thread_type="pr",
                    created_at=pr.created_at,
                    labels=[l.name for l in pr.labels],
                    comments_text=_fetch_comments(pr),
                    **meta,
                )
                threads.append(thread)

            logger.info("  → fetched %d threads from %s", len([t for t in threads if t.repo == repo_name]), repo_name)

        except RateLimitExceededException:
            reset = g.rate_limiting_resettime
            wait = max(0, reset - int(time.time())) + 5
            logger.warning("Rate limit hit. Sleeping %ds ...", wait)
            time.sleep(wait)
        except GithubException as exc:
            logger.error("GitHub error for %s: %s", repo_name, exc)

    logger.info("Total threads fetched: %d", len(threads))
    return threads

def _paginate(query, limit: int) -> Iterator:
    count = 0
    for item in query:
        if count >= limit:
            break
        yield item
        count += 1
""",
    "ingestion/extractor.py": """\"\"\"
extractor.py — Two-stage extraction pipeline modified for OpenAI/Featherless proxy.
\"\"\"
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime

import openai

from ingestion import cache
from ingestion.taxonomy import is_valid_slug, taxonomy_for_prompt

logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    thread_id: str
    problem_label: str | None
    problem_description: str | None
    decision_made: str | None
    outcome_type: str | None
    outcome_description: str | None
    lesson: str | None
    extraction_confidence: float
    evidence_confidence: float
    overall_confidence: float
    confidence_reason: str
    is_regret: bool
    regret_alternative: str | None
    evidence_url: str
    uncertainties: list[str]
    context_team_size: str
    context_project_stage: str
    context_technology_stack: list[str]
    community_size: int
    created_at: datetime
    repo: str
    skipped: bool = False
    skip_reason: str = ""

    @property
    def is_valid(self) -> bool:
        return (
            not self.skipped
            and self.problem_label is not None
            and self.overall_confidence >= 0.3
        )

_STAGE1_SYSTEM = "You are an engineering decision analyst. Extract raw candidates from GitHub threads. Return only valid JSON. No markdown. No explanation."

_STAGE1_USER = \"\"\"Scan this GitHub thread for engineering decisions.

Thread:
{text}

Return exactly:
{{
  "has_engineering_decision": true or false,
  "problem_candidates": ["phrases describing the problem"],
  "decision_candidates": ["what was decided"],
  "outcome_candidates": ["what happened as a result"],
  "evidence_sentences": ["direct quotes supporting a decision"],
  "technologies_mentioned": ["list of tech names"]
}}\"\"\"

_STAGE2_SYSTEM = "You are an engineering decision analyst. Normalize raw candidates into a structured decision record. Return only valid JSON. No markdown. No explanation outside the JSON. Never invent facts not present in the candidates or thread. When uncertain, use low confidence scores and explain in confidence_reason."

_STAGE2_USER = \"\"\"Normalize this engineering decision into a structured record.

Map the problem to exactly ONE slug from this taxonomy:
{taxonomy}

If confidence < 0.5, set problem_label to null.

Raw candidates:
{candidates}

Original thread URL: {url}
Repository: {repo}
Repository stars (community size proxy): {stars}
Created at: {created_at}

Return exactly:
{{
  "problem_label": "slug-from-taxonomy or null",
  "problem_description": "one sentence or null",
  "decision_made": "what was decided or null",
  "outcome_type": "positive|negative|mixed|reverted|unknown",
  "outcome_description": "what happened or null",
  "lesson": "what future teams should know or null",
  "extraction_confidence": 0.0,
  "evidence_confidence": 0.0,
  "overall_confidence": 0.0,
  "confidence_reason": "brief explanation",
  "is_regret": false,
  "regret_alternative": "what they wished they had done or null",
  "uncertainties": ["list of what is unclear"],
  "context_team_size": "small|medium|large|unknown",
  "context_project_stage": "early|growth|mature|unknown"
}}\"\"\"


class Extractor:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.featherless.ai/v1")
        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def _call_llm(self, system: str, user: str, temperature: float = 0.0) -> str:
        msg = self._client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-70B-Instruct"),
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
        )
        return msg.choices[0].message.content.strip()

    def _parse_json(self, raw: str) -> dict:
        cleaned = re.sub(r"^```(?:json)?\\s*|\\s*```$", "", raw.strip(), flags=re.MULTILINE)
        return json.loads(cleaned)

    def _infer_context_from_stars(self, stars: int) -> str:
        if stars > 10_000:
            return "mature"
        if stars > 1_000:
            return "growth"
        return "early"

    def extract(self, thread) -> ExtractionResult:
        cached = cache.get(thread.id)
        if cached is not None:
            return cached

        result = self._extract_fresh(thread)
        cache.set(thread.id, result)
        return result

    def _extract_fresh(self, thread) -> ExtractionResult:
        base = ExtractionResult(
            thread_id=thread.id,
            problem_label=None,
            problem_description=None,
            decision_made=None,
            outcome_type=None,
            outcome_description=None,
            lesson=None,
            extraction_confidence=0.0,
            evidence_confidence=0.0,
            overall_confidence=0.0,
            confidence_reason="extraction failed",
            is_regret=False,
            regret_alternative=None,
            evidence_url=thread.url,
            uncertainties=["extraction failed"],
            context_team_size="unknown",
            context_project_stage=self._infer_context_from_stars(thread.stars),
            context_technology_stack=[],
            community_size=thread.stars,
            created_at=thread.created_at,
            repo=thread.repo,
            skipped=True,
            skip_reason="",
        )

        try:
            raw1 = self._call_llm(_STAGE1_SYSTEM, _STAGE1_USER.format(text=thread.full_text()))
            stage1 = self._parse_json(raw1)
        except Exception as exc:
            base.skip_reason = f"stage1 failed: {exc}"
            return base

        if not stage1.get("has_engineering_decision", False):
            base.skipped = True
            base.skip_reason = "no engineering decision found"
            return base

        technologies = stage1.get("technologies_mentioned", [])

        try:
            raw2 = self._call_llm(
                _STAGE2_SYSTEM,
                _STAGE2_USER.format(
                    taxonomy=taxonomy_for_prompt(),
                    candidates=json.dumps(stage1, indent=2),
                    url=thread.url,
                    repo=thread.repo,
                    stars=thread.stars,
                    created_at=thread.created_at.isoformat(),
                ),
            )
            stage2 = self._parse_json(raw2)
        except Exception as exc:
            base.skip_reason = f"stage2 failed: {exc}"
            return base

        slug = stage2.get("problem_label")
        if slug and not is_valid_slug(slug):
            slug = None

        if not slug:
            base.skipped = True
            base.skip_reason = "problem_label null or invalid slug"
            return base

        ext_conf = float(stage2.get("extraction_confidence", 0.0))
        ev_conf = float(stage2.get("evidence_confidence", 0.0))
        overall = round((ext_conf * 0.5) + (ev_conf * 0.5), 3)

        return ExtractionResult(
            thread_id=thread.id,
            problem_label=slug,
            problem_description=stage2.get("problem_description"),
            decision_made=stage2.get("decision_made"),
            outcome_type=stage2.get("outcome_type", "unknown"),
            outcome_description=stage2.get("outcome_description"),
            lesson=stage2.get("lesson"),
            extraction_confidence=ext_conf,
            evidence_confidence=ev_conf,
            overall_confidence=overall,
            confidence_reason=stage2.get("confidence_reason", ""),
            is_regret=bool(stage2.get("is_regret", False)),
            regret_alternative=stage2.get("regret_alternative"),
            evidence_url=thread.url,
            uncertainties=stage2.get("uncertainties", []),
            context_team_size=stage2.get("context_team_size", "unknown"),
            context_project_stage=stage2.get("context_project_stage", "unknown"),
            context_technology_stack=technologies,
            community_size=thread.stars,
            created_at=thread.created_at,
            repo=thread.repo,
            skipped=False,
        )
""",
    "graph/schema.py": """\"\"\"
schema.py — Node and edge dataclass definitions.
\"\"\"
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
        return "\\n".join(parts)
""",
    "graph/builder.py": """\"\"\"
builder.py — Graph construction via Cognee.
\"\"\"
from __future__ import annotations

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

DATASET_NAME = "edi_decisions"

def _configure_cognee() -> None:
    import cognee
    
    # Let LiteLLM (via cognee) use the provided OPENAI base url + key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "https://api.featherless.ai/v1")
    
    cognee.config.set("llm_provider", "openai")
    cognee.config.set("llm_model", os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-70B-Instruct"))
    cognee.config.set("llm_api_key", os.environ["OPENAI_API_KEY"])
    
    # Vector DB embedding might fail if featherless doesn't have embeddings. 
    # Try using it, if it fails user may need a real OpenAI key for embeddings
    cognee.config.set("embedding_provider", "openai")
    cognee.config.set("embedding_model", "text-embedding-3-small")
    cognee.config.set("vector_db_provider", "lancedb")

async def build_graph(extractions: list) -> dict:
    import cognee
    _configure_cognee()

    valid = [e for e in extractions if e.is_valid]
    logger.info("Building graph: %d valid extractions of %d total", len(valid), len(extractions))

    if not valid:
        return {"total": len(extractions), "ingested": 0, "skipped": len(extractions), "problems_found": 0}

    ingested = 0
    for ext in valid:
        try:
            text = _extraction_to_text(ext)
            await asyncio.wait_for(cognee.remember(text, dataset_name=DATASET_NAME), timeout=60.0)
            ingested += 1
        except Exception as exc:
            logger.warning("Failed to remember %s: %s", ext.thread_id, exc)

    try:
        await asyncio.wait_for(cognee.improve(dataset=DATASET_NAME), timeout=300.0)
    except Exception as exc:
        logger.warning("improve() error (non-fatal): %s", exc)

    problems = len({e.problem_label for e in valid})
    return {
        "total": len(extractions),
        "ingested": ingested,
        "skipped": len(extractions) - ingested,
        "problems_found": problems,
    }

def _extraction_to_text(ext) -> str:
    parts = [
        f"Engineering Decision Record",
        f"Problem Category: {ext.problem_label}",
        f"Repository: {ext.repo}",
        f"Decision Made: {ext.decision_made or 'unspecified'}",
        f"Outcome: {ext.outcome_type} — {ext.outcome_description or ''}",
        f"Lesson Learned: {ext.lesson or 'none recorded'}",
        f"Is Regret Case: {ext.is_regret}",
        f"Regret Alternative: {ext.regret_alternative or 'N/A'}",
        f"Confidence Score: {ext.overall_confidence:.2f}",
        f"Confidence Reason: {ext.confidence_reason}",
        f"Team Size: {ext.context_team_size}",
        f"Project Stage: {ext.context_project_stage}",
        f"Community Size: {ext.community_size} GitHub stars",
        f"Technology Stack: {', '.join(ext.context_technology_stack) or 'unspecified'}",
        f"Year: {ext.created_at.year}",
        f"Evidence URL: {ext.evidence_url}",
    ]
    if ext.uncertainties:
        parts.append(f"Uncertainties: {'; '.join(ext.uncertainties)}")
    return "\\n".join(parts)
""",
    "query/engine.py": """\"\"\"
engine.py — The reasoning engine.
\"\"\"
from __future__ import annotations

import json
import logging
import os
import re
from collections import Counter
from dataclasses import dataclass, field

import openai

from ingestion.taxonomy import PROBLEM_TAXONOMY, get_label, taxonomy_for_prompt

logger = logging.getLogger(__name__)

@dataclass
class RegretCase:
    decision: str
    regret_reason: str
    alternative: str
    evidence_url: str

@dataclass
class QueryResponse:
    problem_slug: str
    problem_label: str
    recurrence_count: int
    similar_cases: int
    dominant_outcome: str
    outcome_breakdown: dict[str, int]
    decisions: list[str]
    lessons: list[str]
    regret_cases: list[RegretCase]
    evidence: list[str]
    temporal_trend: list[dict]
    overall_confidence: float
    uncertainties: list[str]
    answer: str
    raw_records: list[dict] = field(default_factory=list, repr=False)

class QueryEngine:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.featherless.ai/v1")
        self._client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-70B-Instruct")

    async def query(self, description: str, context: dict | None = None) -> QueryResponse:
        slug = await self._identify_problem_slug(description, context)
        raw_results = await self._recall_from_cognee(slug, description)
        records = self._parse_recall_results(raw_results)
        aggregated = self._aggregate(records, slug)
        answer = await self._synthesize_answer(description, context, aggregated)

        return QueryResponse(
            problem_slug=slug,
            problem_label=get_label(slug),
            recurrence_count=aggregated["recurrence_count"],
            similar_cases=aggregated["similar_cases"],
            dominant_outcome=aggregated["dominant_outcome"],
            outcome_breakdown=aggregated["outcome_breakdown"],
            decisions=aggregated["decisions"][:5],
            lessons=aggregated["lessons"][:5],
            regret_cases=aggregated["regret_cases"][:3],
            evidence=aggregated["evidence"][:8],
            temporal_trend=aggregated["temporal_trend"],
            overall_confidence=aggregated["overall_confidence"],
            uncertainties=aggregated["uncertainties"][:5],
            answer=answer,
            raw_records=records[:10],
        )

    async def _identify_problem_slug(self, description: str, context: dict | None) -> str:
        ctx_str = json.dumps(context or {}, indent=2)
        prompt = f"Map this engineering problem to the most fitting slug from the taxonomy.\\nProblem description: {description}\\nUser context: {ctx_str}\\n\\nTaxonomy:\\n{taxonomy_for_prompt()}\\n\\nReturn ONLY the slug string, nothing else. No explanation. No quotes. If nothing fits, return: database-selection"

        try:
            msg = await self._client.chat.completions.create(
                model=self._model,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
            )
            slug = msg.choices[0].message.content.strip().lower().strip('"\\'')
            return slug if slug in PROBLEM_TAXONOMY else "database-selection"
        except Exception as exc:
            logger.warning("Slug identification failed: %s", exc)
            return "database-selection"

    async def _recall_from_cognee(self, slug: str, description: str) -> list:
        import cognee
        query = f"Engineering decisions about {get_label(slug)}: {description}"
        try:
            results = await cognee.recall(query_text=query, top_k=20, auto_route=True)
            return results or []
        except Exception as exc:
            logger.warning("cognee.recall() failed: %s", exc)
            return []

    def _parse_recall_results(self, results: list) -> list[dict]:
        records = []
        for result in results:
            try:
                text = self._extract_text_from_result(result)
                if not text:
                    continue
                record = self._parse_decision_text(text)
                if record:
                    records.append(record)
            except Exception as exc:
                pass
        return records

    def _extract_text_from_result(self, result) -> str:
        if hasattr(result, "answer"): return str(result.answer or "")
        if hasattr(result, "text"): return str(result.text or "")
        if hasattr(result, "content"):
            c = result.content
            return " ".join(str(i) for i in c) if isinstance(c, list) else str(c or "")
        if hasattr(result, "source"): return str(result.source or "")
        return str(result)

    def _parse_decision_text(self, text: str) -> dict | None:
        if "Problem Category:" not in text and "PROBLEM:" not in text:
            return None

        def extract(pattern: str, default: str = "") -> str:
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(1).strip() if m else default

        outcome_raw = extract(r"Outcome:\\s*(\\w+)")
        is_regret = "true" in extract(r"Is Regret Case:\\s*(\\w+)").lower()
        year_str = extract(r"Year:\\s*(\\d{4})")

        return {
            "problem": extract(r"Problem Category:\\s*(.+)"),
            "repo": extract(r"Repository:\\s*(.+)"),
            "decision": extract(r"Decision Made:\\s*(.+)"),
            "outcome_type": outcome_raw if outcome_raw in ("positive", "negative", "mixed", "reverted") else "unknown",
            "outcome_desc": extract(r"Outcome:.*?—\\s*(.+)"),
            "lesson": extract(r"Lesson Learned:\\s*(.+)"),
            "is_regret": is_regret,
            "regret_alt": extract(r"Regret Alternative:\\s*(.+)"),
            "confidence": float(extract(r"Confidence Score:\\s*([\\d.]+)") or "0"),
            "team_size": extract(r"Team Size:\\s*(\\w+)"),
            "stage": extract(r"Project Stage:\\s*(\\w+)"),
            "tech": extract(r"Technology Stack:\\s*(.+)"),
            "year": int(year_str) if year_str else 0,
            "evidence_url": extract(r"Evidence URL:\\s*(https?://\\S+)"),
            "uncertainties": extract(r"Uncertainties:\\s*(.+)"),
        }

    def _aggregate(self, records: list[dict], slug: str) -> dict:
        if not records:
            return {
                "recurrence_count": 0,
                "similar_cases": 0,
                "dominant_outcome": "unknown",
                "outcome_breakdown": {},
                "decisions": [],
                "lessons": [],
                "regret_cases": [],
                "evidence": [],
                "temporal_trend": [],
                "overall_confidence": 0.0,
                "uncertainties": ["No matching records found in graph. Run /ingest first."],
            }

        relevant = [r for r in records if slug in r.get("problem", "").lower() or True]
        outcome_counts = Counter(r["outcome_type"] for r in relevant if r.get("outcome_type"))
        dominant = outcome_counts.most_common(1)[0][0] if outcome_counts else "unknown"

        lesson_counter = Counter()
        for r in relevant:
            if r.get("lesson") and r["lesson"] not in ("none recorded", "N/A", ""):
                lesson_counter[r["lesson"]] += 1
        lessons = [l for l, _ in lesson_counter.most_common(5)]

        decisions = list({r["decision"] for r in relevant if r.get("decision") and r["decision"] != "unspecified"})[:5]

        regret_cases = []
        for r in relevant:
            if r.get("is_regret") and r.get("decision"):
                regret_cases.append(RegretCase(
                    decision=r["decision"],
                    regret_reason=r.get("outcome_desc", ""),
                    alternative=r.get("regret_alt", "unknown"),
                    evidence_url=r.get("evidence_url", ""),
                ))

        evidence = list({r["evidence_url"] for r in relevant if r.get("evidence_url") and r["evidence_url"].startswith("https://")})

        year_counter = Counter(r["year"] for r in relevant if r.get("year", 0) > 2000)
        temporal_trend = sorted([{"year": y, "count": c} for y, c in year_counter.items()], key=lambda x: x["year"])

        confidences = [r["confidence"] for r in relevant if r.get("confidence", 0) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        all_uncertainties = []
        for r in relevant:
            if r.get("uncertainties"):
                all_uncertainties.extend(r["uncertainties"].split(";"))
        unique_uncertainties = list({u.strip() for u in all_uncertainties if u.strip()})[:5]

        return {
            "recurrence_count": len(relevant),
            "similar_cases": len(relevant),
            "dominant_outcome": dominant,
            "outcome_breakdown": dict(outcome_counts),
            "decisions": decisions,
            "lessons": lessons,
            "regret_cases": regret_cases,
            "evidence": evidence,
            "temporal_trend": temporal_trend,
            "overall_confidence": round(avg_confidence, 2),
            "uncertainties": unique_uncertainties,
        }

    async def _synthesize_answer(self, description: str, context: dict | None, aggregated: dict) -> str:
        if aggregated["recurrence_count"] == 0:
            return "No matching engineering decisions found in the graph for this query. Run POST /ingest with your target repositories to build the knowledge graph first."

        ctx_str = json.dumps(context or {})
        agg_str = json.dumps({k: v for k, v in aggregated.items() if k not in ("regret_cases", "raw_records")}, indent=2)

        prompt = f"You are an engineering decision analyst. Write a concise, grounded answer.\\nUser's problem: {description}\\nUser's context: {ctx_str}\\nAggregated graph data:\\n{agg_str}\\nRules:\\n- Only state facts supported by the aggregated data\\n- Never invent numbers or outcomes not in the data\\n- If recurrence_count is low (< 5), acknowledge limited data\\n- Mention dominant outcome, key lessons, and regret cases if present\\n- End with the strongest actionable recommendation\\n- Keep it under 150 words\\n- Write in plain, direct language — no fluff\\n\\nAnswer:"

        try:
            msg = await self._client.chat.completions.create(
                model=self._model,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.choices[0].message.content.strip()
        except Exception as exc:
            logger.warning("Synthesis failed: %s", exc)
            return f"Graph found {aggregated['recurrence_count']} matching cases. Dominant outcome: {aggregated['dominant_outcome']}. Top lesson: {aggregated['lessons'][0] if aggregated['lessons'] else 'none recorded'}."


async def get_all_problems() -> list[dict]:
    import cognee
    try:
        results = await cognee.recall(query_text="engineering decision problems repository lessons outcomes", top_k=50, auto_route=True)
    except Exception as exc:
        logger.warning("get_all_problems recall failed: %s", exc)
        return []

    engine = QueryEngine.__new__(QueryEngine)
    records = engine._parse_recall_results(results)

    problem_map: dict[str, dict] = {}
    for r in records:
        slug = r.get("problem", "").strip()
        if not slug: continue
        if slug not in problem_map:
            problem_map[slug] = {"slug": slug, "label": get_label(slug), "recurrence_count": 0, "outcomes": Counter(), "lessons": [], "repos": set(), "years": []}
        p = problem_map[slug]
        p["recurrence_count"] += 1
        if r.get("outcome_type"): p["outcomes"][r["outcome_type"]] += 1
        if r.get("lesson") and r["lesson"] not in ("none recorded", ""): p["lessons"].append(r["lesson"])
        if r.get("repo"): p["repos"].add(r["repo"])
        if r.get("year", 0) > 2000: p["years"].append(r["year"])

    result = []
    for slug, p in sorted(problem_map.items(), key=lambda x: -x[1]["recurrence_count"]):
        dominant = p["outcomes"].most_common(1)[0][0] if p["outcomes"] else "unknown"
        top_lesson = Counter(p["lessons"]).most_common(1)
        result.append({
            "slug": slug,
            "label": get_label(slug),
            "recurrence_count": p["recurrence_count"],
            "dominant_outcome": dominant,
            "top_lesson": top_lesson[0][0] if top_lesson else None,
            "repos": sorted(p["repos"]),
            "last_seen": max(p["years"]) if p["years"] else None,
        })
    return result
""",
    "models.py": """\"\"\"
models.py — Pydantic request/response models.
\"\"\"
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
""",
    "main.py": """\"\"\"
main.py — Engineering Decision Intelligence API
\"\"\"
from __future__ import annotations
import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))

from models import (IngestRequest, IngestResponse, QueryRequest, QueryResponse, RegretCaseOut, TemporalPoint, ProblemSummary, HealthResponse)
from ingestion import cache
from ingestion.github import fetch_threads
from ingestion.extractor import Extractor
from graph.builder import build_graph
from query.engine import QueryEngine, get_all_problems

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("edi.main")

_ingest_lock = asyncio.Lock()
_ingest_status: dict = {"running": False, "last_result": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("EDI starting")
    yield
    logger.info("EDI shutting down")

app = FastAPI(title="Engineering Decision Intelligence", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_ui():
    ui_path = Path(__file__).parent / "static" / "index.html"
    if ui_path.exists(): return HTMLResponse(ui_path.read_text())
    return HTMLResponse("<h1>EDI</h1><p>UI not found. See /docs</p>")

@app.get("/health", response_model=HealthResponse)
async def health():
    import cognee
    graph_ready = False
    try:
        results = await asyncio.wait_for(cognee.recall("engineering decision", top_k=1), timeout=5.0)
        graph_ready = len(results) > 0
    except Exception: pass
    return HealthResponse(status="ok", version="1.0.0", cognee_version=cognee.__version__, cache_stats=cache.stats(), graph_ready=graph_ready)

@app.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest):
    if _ingest_status["running"]: raise HTTPException(409, "Ingestion already running.")
    async with _ingest_lock:
        _ingest_status["running"] = True
        try: return await _run_ingest(req)
        finally: _ingest_status["running"] = False

async def _run_ingest(req: IngestRequest) -> IngestResponse:
    repo_name = req.repo_name
    github_token = os.getenv("GITHUB_TOKEN", "")
    if not github_token or github_token == "your_github_token": raise HTTPException(422, "GITHUB_TOKEN not set in .env")
    
    threads = await asyncio.to_thread(fetch_threads, repo_names=[repo_name], max_per_repo=req.max_issues, token=github_token)
    if not threads: raise HTTPException(404, "No threads found")

    extractor = Extractor()
    extractions = []
    cache_hits = 0
    for thread in threads:
        hit_before = cache.exists(thread.id)
        ext = await asyncio.to_thread(extractor.extract, thread)
        extractions.append(ext)
        if hit_before: cache_hits += 1

    valid = [e for e in extractions if e.is_valid]
    if not valid:
        return IngestResponse(status="completed_no_decisions", repo=repo_name, threads_fetched=len(threads), threads_ingested=0, threads_skipped=len(extractions), problems_found=0, cached_hits=cache_hits, message="No engineering decisions extracted.")

    build_result = await build_graph(extractions)
    return IngestResponse(status="completed", repo=repo_name, threads_fetched=len(threads), threads_ingested=build_result["ingested"], threads_skipped=build_result["skipped"], problems_found=build_result["problems_found"], cached_hits=cache_hits, message="Graph built.")

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    engine = QueryEngine()
    result = await engine.query(description=req.description, context=req.context.model_dump() if req.context else None)
    return QueryResponse(
        problem_slug=result.problem_slug, problem_label=result.problem_label, recurrence_count=result.recurrence_count, similar_cases=result.similar_cases, dominant_outcome=result.dominant_outcome, outcome_breakdown=result.outcome_breakdown, decisions=result.decisions, lessons=result.lessons,
        regret_cases=[RegretCaseOut(decision=r.decision, regret_reason=r.regret_reason, alternative=r.alternative, evidence_url=r.evidence_url) for r in result.regret_cases],
        evidence=result.evidence, temporal_trend=[TemporalPoint(year=p["year"], count=p["count"]) for p in result.temporal_trend],
        overall_confidence=result.overall_confidence, uncertainties=result.uncertainties, answer=result.answer,
    )

@app.get("/problems", response_model=list[ProblemSummary])
async def problems():
    raw = await get_all_problems()
    return [ProblemSummary(slug=p["slug"], label=p["label"], recurrence_count=p["recurrence_count"], dominant_outcome=p["dominant_outcome"], top_lesson=p.get("top_lesson"), repos=p.get("repos", []), last_seen=p.get("last_seen")) for p in raw]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="warning")
"""
}

for rel_path, content in FILES.items():
    p = BASE_DIR / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully applied the comprehensive codebase at {BASE_DIR}")
