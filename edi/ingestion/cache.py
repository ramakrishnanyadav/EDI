"""
cache.py — Pickle cache for extraction results.

Keyed by thread ID. Every ingestion run is restartable from any crash point.
"""
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
