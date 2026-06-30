import pytest
from datetime import datetime, timezone
from edi.ingestion.extractor import Extractor, ExtractionResult
from edi.ingestion.github import GitHubThread

@pytest.fixture
def mock_thread():
    return GitHubThread(
        id="test/repo#1/issue",
        repo="test/repo",
        repo_url="https://github.com/test/repo",
        number=1,
        title="Migrate to LanceDB",
        body="We need faster vector search",
        url="https://github.com/test/repo/issues/1",
        thread_type="issue",
        created_at=datetime.now(timezone.utc),
        labels=["database"],
        comments_text="Let's do it",
        stars=5000,
        forks=100,
        contributors_count=50
    )

def test_infer_context_from_stars(mock_thread):
    extractor = Extractor()
    assert extractor._infer_context_from_stars(mock_thread.stars) == "growth"
    assert extractor._infer_context_from_stars(500) == "early"
    assert extractor._infer_context_from_stars(20000) == "mature"
