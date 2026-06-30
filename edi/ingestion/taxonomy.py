"""
taxonomy.py — Canonical problem taxonomy.

The single most important file in the project.
Every extracted problem maps to one slug here or is marked unknown.
Locked — never add slugs during ingestion, only via human review.
"""
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
    return "\n".join(lines)
