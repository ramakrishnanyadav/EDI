"""
builder.py — Graph construction via Cognee.
"""
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
    return "\n".join(parts)
