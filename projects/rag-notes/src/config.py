"""Centralized configuration loaded from environment variables.

All defaults are tuned for the PoC. Override values via a `.env` file at the
project root or via real environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Load .env from project root if present. Safe to call when the file is absent.
load_dotenv(PROJECT_ROOT / ".env")


def _resolve_path(value: str, default: Path) -> Path:
    """Resolve a path env var. Accepts relative paths anchored at PROJECT_ROOT."""
    raw = os.getenv(value, str(default))
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (PROJECT_ROOT / p).resolve()
    return p


NOTES_PATH: Path = _resolve_path("NOTES_PATH", PROJECT_ROOT / "data" / "sample_notes")
CHROMA_PATH: str = os.getenv("CHROMA_PATH", str(PROJECT_ROOT / "chroma_db"))
# When set, the pipeline uses a ChromaDB server (HttpClient) instead of the
# embedded PersistentClient. Leave empty for the default local-only setup.
CHROMA_URL: str | None = os.getenv("CHROMA_URL") or None
COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "private_notes")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.1")

TOP_K: int = int(os.getenv("TOP_K", "4"))
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "120"))