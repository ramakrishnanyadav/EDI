import requests
import json
import time

print("Starting ingestion for langchain-ai/langchain (max 10 issues)...")
try:
    res = requests.post(
        "http://localhost:8004/ingest",
        json={"repo_url": "https://github.com/langchain-ai/langchain", "max_issues": 10},
        timeout=180
    )
    print("Ingest Response:")
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(f"Ingestion failed: {e}")

print("\nRunning query to fetch results...")
try:
    # We don't know exactly which problem slug was extracted, let's query for "database" to catch any
    res = requests.post(
        "http://localhost:8004/query",
        json={
            "description": "database",
            "context": {"team_size": "medium"}
        }
    )
    data = res.json()
    print("\n--- Query Results ---")
    print(f"Problem: {data.get('problem_label')}")
    print(f"Recurrence: {data.get('recurrence_count')}")
    print(f"Dominant Outcome: {data.get('dominant_outcome')}")
    
    print("\nDecisions:")
    for d in data.get('decisions', []):
        print(f"- {d}")
        
    print("\nRegret Cases:")
    for r in data.get('regret_cases', []):
        print(f"- Decision: {r['decision']}, Reason: {r['regret_reason']}, Alt: {r['alternative']}")
        
    print("\nEvidence URLs:")
    for e in data.get('evidence', []):
        print(f"- {e}")
        
    print("\nAnswer:")
    print(data.get('answer'))
except Exception as e:
    print(f"Query failed: {e}")
