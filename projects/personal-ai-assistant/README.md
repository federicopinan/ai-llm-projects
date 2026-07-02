# Context-Aware Personal AI Assistant

A workflow-based AI assistant proof of concept designed to support daily planning, research summarization, task breakdown, and decision support using reusable prompt templates and structured context.

## Overview

This project explores how a small set of well-designed prompt workflows can act as a personal AI assistant without requiring a heavy application stack.

Instead of building an autonomous agent, this PoC focuses on the **layer below the LLM**: how to define reusable workflows as markdown templates, inject user context, and produce structured prompts the user can execute against any model.

The default mode is **prompt-only**: the assistant generates the structured prompt, prints it, and lets the user review it before sending it to an LLM.

## Problem

Most personal AI usage today is reactive: the user opens a chat window, types a vague question, gets a vague answer, and repeats the same prompt structure dozens of times.

The friction is not the model — it is the **absence of reusable structure**. Each session starts from zero. There is no shared template for "help me plan my day", no consistent format for "summarize this research", no repeatable decision framework.

This PoC addresses that gap by treating prompt workflows as **first-class artifacts**: versionable, inspectable, and editable in plain markdown.

## Goals

- Define reusable prompt workflows as plain markdown files
- Inject structured context (available time, goals, constraints) into each workflow
- Produce deterministic, reviewable structured prompts
- Support a prompt-only mode that requires no LLM backend
- Optionally forward the prompt to a local Ollama instance
- Keep the assistant non-autonomous by default: humans review every output

## Architecture

```txt
User objective
      ↓
Workflow selection (markdown file)
      ↓
Prompt template + context fields
      ↓
Context injection (CLI flags or stdin)
      ↓
Final structured prompt
      ↓
LLM backend (optional)
      ↓
Reviewable output
```

The full architectural rationale is documented in [`docs/architecture.md`](docs/architecture.md).

## Core Workflows

The assistant ships with four workflows, each defined as a markdown file under `workflows/`:

| Workflow             | Purpose                                                    |
|----------------------|------------------------------------------------------------|
| `daily-planning`     | Build a realistic daily execution plan from available time |
| `research-assistant` | Summarize technical material without inventing claims      |
| `task-breakdown`     | Convert vague goals into executable tasks                  |
| `decision-support`   | Compare options with pros, cons, risks, and trade-offs      |

See [`docs/workflows.md`](docs/workflows.md) for when to use each one and [`workflows/`](workflows/) for the templates themselves.

## Tech Stack

- **Python 3.10+** — runtime for the CLI
- **Markdown** — workflow and prompt definitions
- **python-dotenv** — environment configuration
- **requests** — optional Ollama HTTP client
- **Ollama** (optional) — local LLM backend

No frameworks, no vector databases, no agent runtimes. The point of this PoC is to keep the prompt layer visible and editable.

## How to Run

```bash
cd projects/personal-ai-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

python src/assistant.py --list
```

Run a workflow with context:

```bash
python src/assistant.py \
  --workflow daily-planning \
  --input "I have 3 hours today. I need to review SIEM alerts, document my RAG project, train, and study one MITRE ATT&CK technique."
```

Run a workflow with structured context fields:

```bash
python src/assistant.py \
  --workflow daily-planning \
  --context available_time=3h \
  --context priorities="SIEM review, RAG docs, training, MITRE ATT&CK" \
  --context energy=medium
```

Send the prompt to a local Ollama instance:

```bash
# Start Ollama locally and pull a model first
ollama serve &
ollama pull llama3.1

# Set ASSISTANT_MODE=ollama in .env, then:
python src/assistant.py \
  --workflow research-assistant \
  --input "RAG systems combine retrieval with generation to ground LLM outputs."
```

## Example Usage

The [`examples/`](examples/) directory contains a complete worked example:

- [`examples/sample-prompt.md`](examples/sample-prompt.md) — realistic user input
- [`examples/sample-output.md`](examples/sample-output.md) — realistic structured assistant output

## Security and Privacy Notes

- **No telemetry.** The CLI does not phone home and does not log conversations.
- **No data persistence.** Generated prompts are printed to stdout. Nothing is written to disk unless the user explicitly redirects output.
- **Synthetic examples only.** All sample prompts and outputs in this repository use invented, non-personal scenarios.
- **Local-first by default.** The default mode (`prompt-only`) does not contact any external service.
- **Local LLM optional.** If `ASSISTANT_MODE=ollama` is set, prompts are sent to a local Ollama instance at `OLLAMA_BASE_URL`. No cloud API is used.
- **Never commit `.env`.** The `.env.example` file documents the variables; secrets and credentials must never be committed.
- **Human review required.** Every workflow output is intended to be reviewed by the user before being acted on. The assistant does not execute actions autonomously.

## Limitations

This is a PoC. It is intentionally limited. See [`docs/limitations.md`](docs/limitations.md) for the full list.

Short version:

- No persistent memory between sessions
- No calendar, email, or task-system integration
- No authentication or multi-user support
- No autonomous action execution
- Output quality depends entirely on the underlying LLM
- The prompt templates are static — there is no automatic prompt optimization

## Future Improvements

- Optional structured memory layer for recurring users
- Calendar and task-system integrations behind an explicit opt-in
- Pluggable LLM backends (OpenAI, Anthropic, local)
- Prompt evaluation suite with deterministic test cases
- Workflow composer: combine multiple workflows in a single run
- Web UI for non-CLI users

## Status

**PoC / Experimental.**

This project is a working proof of concept. It is suitable for personal experimentation and as a portfolio artifact. It is **not** production-ready and should not be wired into critical workflows without significant additional hardening.