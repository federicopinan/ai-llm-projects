"""Configuration loader for the Personal AI Assistant CLI.

Reads .env values via python-dotenv and exposes them as module-level
constants. Values are loaded once at import time.

If a .env file does not exist, defaults are used.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")
ASSISTANT_MODE = os.getenv("ASSISTANT_MODE", "prompt-only").strip().lower()

WORKFLOWS_DIR = PROJECT_ROOT / "workflows"

SUPPORTED_MODES = {"prompt-only", "ollama"}


def describe_mode() -> str:
    """Return a human-readable description of the current mode."""
    if ASSISTANT_MODE == "prompt-only":
        return (
            "prompt-only: the assistant will generate and print a structured prompt. "
            "No LLM call will be made."
        )
    if ASSISTANT_MODE == "ollama":
        return (
            f"ollama: the assistant will send the prompt to {OLLAMA_BASE_URL} "
            f"using model '{LLM_MODEL}'."
        )
    return (
        f"unknown mode '{ASSISTANT_MODE}'. "
        f"Supported modes: {sorted(SUPPORTED_MODES)}. "
        "Falling back to prompt-only."
    )