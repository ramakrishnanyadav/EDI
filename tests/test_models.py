import pytest
from pydantic import ValidationError
from edi.models import IngestRequest, QueryRequest, QueryContext

def test_ingest_request_validation():
    # Valid request
    req = IngestRequest(repo_url="https://github.com/langchain-ai/langchain", max_issues=50)
    assert req.repo_name == "langchain-ai/langchain"
    assert req.max_issues == 50

    # Invalid max_issues (too small)
    with pytest.raises(ValidationError):
        IngestRequest(repo_url="https://github.com/langchain-ai/langchain", max_issues=5)
        
    # Invalid max_issues (too large)
    with pytest.raises(ValidationError):
        IngestRequest(repo_url="https://github.com/langchain-ai/langchain", max_issues=300)

def test_query_request_validation():
    # Valid request
    req = QueryRequest(description="database migration strategy", context=QueryContext(team_size="medium"))
    assert req.description == "database migration strategy"
    assert req.context.team_size == "medium"
    
    # Description too short
    with pytest.raises(ValidationError):
        QueryRequest(description="db")
