"""Workflow loader for the Personal AI Assistant CLI.

Reads workflow markdown files from the workflows/ directory, extracts
the prompt template section, and renders it with user-supplied context.

The loader is intentionally simple. It does not parse YAML front matter
or call out to any templating engine — workflows are plain markdown and
placeholders are `{{key}}` strings.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Allow importing config when workflow_loader.py is loaded directly
# (e.g. via tests) or via assistant.py's sys.path manipulation.
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from config import WORKFLOWS_DIR  # noqa: E402

PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


@dataclass
class Workflow:
    """A loaded workflow with its prompt template rendered."""

    name: str
    path: Path
    purpose: str
    prompt_template: str
    rendered_prompt: str
    missing_placeholders: list[str]


def _split_sections(markdown: str) -> dict[str, str]:
    """Split a markdown document into top-level sections by H2 header."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in markdown.splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _extract_purpose(sections: dict[str, str]) -> str:
    purpose = sections.get("purpose", "")
    return purpose.strip()


def _extract_prompt_template(sections: dict[str, str]) -> str:
    """Extract the prompt template from the workflow markdown.

    The template lives under the `## Prompt Template` section, inside a
    fenced code block. If no fenced block is present, the section body
    is returned as-is so workflows can still be rendered.
    """
    section = sections.get("prompt template", "")
    match = re.search(r"```(?:markdown|text|.*?)\n(.*?)```", section, re.DOTALL)
    if match:
        return match.group(1).strip()
    return section.strip()


def _extract_template_placeholders(template: str) -> set[str]:
    return set(PLACEHOLDER_PATTERN.findall(template))


def _render_template(template: str, context: dict[str, str]) -> tuple[str, list[str]]:
    """Substitute {{key}} placeholders with values from context.

    Returns the rendered prompt and a list of placeholders that were
    present in the template but not provided in the context. Missing
    placeholders are left verbatim in the output so the user can see
    what was not supplied.
    """
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in context and context[key] != "":
            return context[key]
        if key not in missing:
            missing.append(key)
        return match.group(0)

    rendered = PLACEHOLDER_PATTERN.sub(replace, template)
    return rendered, missing


def list_workflows() -> list[Path]:
    """Return the paths of all workflow markdown files in the workflows dir."""
    if not WORKFLOWS_DIR.exists():
        return []
    return sorted(p for p in WORKFLOWS_DIR.glob("*.md") if p.is_file())


def workflow_name_from_path(path: Path) -> str:
    """Derive a workflow name from its filename (without .md)."""
    return path.stem


def load_workflow(name: str) -> Workflow:
    """Load a workflow by name and render it with an empty context.

    The returned Workflow has both the raw template and the rendered
    prompt. Callers should call `render_workflow` after supplying
    context if they want to override the initial render.
    """
    path = WORKFLOWS_DIR / f"{name}.md"
    if not path.exists():
        available = ", ".join(workflow_name_from_path(p) for p in list_workflows())
        raise FileNotFoundError(
            f"Workflow '{name}' not found. Available workflows: {available or '(none)'}"
        )

    markdown = path.read_text(encoding="utf-8")
    sections = _split_sections(markdown)
    purpose = _extract_purpose(sections)
    template = _extract_prompt_template(sections)

    rendered, missing = _render_template(template, {})

    return Workflow(
        name=name,
        path=path,
        purpose=purpose,
        prompt_template=template,
        rendered_prompt=rendered,
        missing_placeholders=missing,
    )


def render_workflow(workflow: Workflow, context: dict[str, str]) -> Workflow:
    """Return a copy of the workflow with its prompt rendered against `context`."""
    rendered, missing = _render_template(workflow.prompt_template, context)
    return Workflow(
        name=workflow.name,
        path=workflow.path,
        purpose=workflow.purpose,
        prompt_template=workflow.prompt_template,
        rendered_prompt=rendered,
        missing_placeholders=missing,
    )