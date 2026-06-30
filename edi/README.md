# Engineering Decision Intelligence (EDI)

*Software teams write code. They lose the reasoning. We remember it.*

EDI is a causal graph memory system built for the WeMakeDevs × Cognee hackathon. It extracts, standardizes, and interconnects the engineering decisions hidden within GitHub issues and PRs, allowing teams to ask: **"What happened to other teams when they faced this exact problem?"**

## Core Innovation
Unlike standard RAG, which retrieves similar text, EDI builds a **causal knowledge graph**:
`Problem → Decision → Outcome → Lesson → Regret`

This allows true reasoning over historical engineering choices.

## Features
- **Two-Stage Extraction:** Uses Claude to accurately extract and normalize problems against a strict taxonomy.
- **Causal Graph Memory:** Powered by Cognee, linking Contexts, Decisions, and Outcomes.
- **Regret Modeling:** Explicitly models `LED_TO_REGRET` edges for negative paths.
- **Temporal Trends:** Understands how architectural thinking evolves over time.
- **Zero-Infra:** Runs entirely on embedded LanceDB and Kuzu databases.

## Setup
1. `pip install -r requirements.txt`
2. Add your `.env` with `GITHUB_TOKEN` and `ANTHROPIC_API_KEY`
3. `uvicorn main:app --reload`
4. Visit `http://localhost:8000` for the dashboard.
