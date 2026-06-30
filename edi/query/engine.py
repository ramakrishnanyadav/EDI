"""
engine.py — The reasoning engine.
"""
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
        prompt = f"Map this engineering problem to the most fitting slug from the taxonomy.\nProblem description: {description}\nUser context: {ctx_str}\n\nTaxonomy:\n{taxonomy_for_prompt()}\n\nReturn ONLY the slug string, nothing else. No explanation. No quotes. If nothing fits, return: database-selection"

        try:
            msg = await self._client.chat.completions.create(
                model=self._model,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
            )
            slug = msg.choices[0].message.content.strip().lower().strip('"\'')
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

        outcome_raw = extract(r"Outcome:\s*(\w+)")
        is_regret = "true" in extract(r"Is Regret Case:\s*(\w+)").lower()
        year_str = extract(r"Year:\s*(\d{4})")

        return {
            "problem": extract(r"Problem Category:\s*(.+)"),
            "repo": extract(r"Repository:\s*(.+)"),
            "decision": extract(r"Decision Made:\s*(.+)"),
            "outcome_type": outcome_raw if outcome_raw in ("positive", "negative", "mixed", "reverted") else "unknown",
            "outcome_desc": extract(r"Outcome:.*?—\s*(.+)"),
            "lesson": extract(r"Lesson Learned:\s*(.+)"),
            "is_regret": is_regret,
            "regret_alt": extract(r"Regret Alternative:\s*(.+)"),
            "confidence": float(extract(r"Confidence Score:\s*([\d.]+)") or "0"),
            "team_size": extract(r"Team Size:\s*(\w+)"),
            "stage": extract(r"Project Stage:\s*(\w+)"),
            "tech": extract(r"Technology Stack:\s*(.+)"),
            "year": int(year_str) if year_str else 0,
            "evidence_url": extract(r"Evidence URL:\s*(https?://\S+)"),
            "uncertainties": extract(r"Uncertainties:\s*(.+)"),
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

        relevant = [r for r in records if slug in r.get("problem", "").lower()]
        outcome_counts = Counter(r["outcome_type"] for r in relevant if r.get("outcome_type"))
        dominant = outcome_counts.most_common(1)[0][0] if outcome_counts else "unknown"

        lesson_counter = Counter()
        for r in relevant:
            if r.get("lesson") and r["lesson"] not in ("none recorded", "N/A", ""):
                lesson_counter[r["lesson"]] += 1
        lessons = [lesson for lesson, _ in lesson_counter.most_common(5)]

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
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        evidence_count = len(evidence)
        recurrence_count = len(relevant)
        
        evidence_score = min(evidence_count / 10.0, 1.0)
        recurrence_score = min(recurrence_count / 5.0, 1.0)
        extraction_score = min(avg_confidence, 1.0)
        
        overall_confidence = (evidence_score * 0.4) + (recurrence_score * 0.3) + (extraction_score * 0.3)

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
            "overall_confidence": round(overall_confidence, 2),
            "evidence_score": round(evidence_score, 2),
            "recurrence_score": round(recurrence_score, 2),
            "extraction_score": round(extraction_score, 2),
            "uncertainties": unique_uncertainties,
        }

    async def _synthesize_answer(self, description: str, context: dict | None, aggregated: dict) -> str:
        if aggregated["recurrence_count"] == 0:
            return "No matching engineering decisions found in the graph for this query. Run POST /ingest with your target repositories to build the knowledge graph first."

        ctx_str = json.dumps(context or {})
        agg_str = json.dumps({k: v for k, v in aggregated.items() if k not in ("regret_cases", "raw_records")}, indent=2)

        prompt = f"You are an engineering decision analyst. Write a concise, grounded answer.\nUser's problem: {description}\nUser's context: {ctx_str}\nAggregated graph data:\n{agg_str}\nRules:\n- Only state facts supported by the aggregated data\n- Never invent numbers or outcomes not in the data\n- If recurrence_count is low (< 5), acknowledge limited data\n- Mention dominant outcome, key lessons, and regret cases if present\n- End with the strongest actionable recommendation\n- Keep it under 150 words\n- Write in plain, direct language — no fluff\n\nAnswer:"

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
