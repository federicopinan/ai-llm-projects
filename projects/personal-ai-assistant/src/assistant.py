"""CLI entry point for the Personal AI Assistant PoC.

Usage:
    python src/assistant.py --list
    python src/assistant.py --workflow <name> --input "<text>"
    python src/assistant.py --workflow <name> --context key=value [--context ...]

The CLI:
- Lists available workflows from the workflows/ directory.
- Loads the selected workflow's markdown template.
- Substitutes user context into the template's placeholders.
- Prints the rendered prompt.
- Optionally forwards the prompt to a local Ollama instance when
  ASSISTANT_MODE=ollama is configured.

If no LLM backend is configured, the CLI prints the generated prompt
and explains that no LLM backend is configured. It does not fail.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running this file directly with `python src/assistant.py` by ensuring
# the src/ directory is on sys.path. This avoids forcing the user to invoke
# the CLI as `python -m src.assistant`.
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from config import ASSISTANT_MODE, LLM_MODEL, OLLAMA_BASE_URL, SUPPORTED_MODES, describe_mode  # noqa: E402
from workflow_loader import (  # noqa: E402
    Workflow,
    list_workflows,
    load_workflow,
    render_workflow,
    workflow_name_from_path,
)


def _print_workflows() -> None:
    paths = list_workflows()
    if not paths:
        print("No workflows found in the workflows/ directory.")
        return
    print("Available workflows:\n")
    for path in paths:
        name = workflow_name_from_path(path)
        try:
            workflow = load_workflow(name)
            purpose_first_line = workflow.purpose.splitlines()[0] if workflow.purpose else ""
        except Exception:  # noqa: BLE001
            purpose_first_line = "(could not load purpose)"
        print(f"  - {name}")
        if purpose_first_line:
            print(f"      {purpose_first_line}")
    print(f"\nMode: {describe_mode()}")


def _parse_context(items: list[str]) -> dict[str, str]:
    """Parse repeated `--context key=value` flags into a dict."""
    context: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            print(f"warning: ignoring malformed --context '{item}' (expected key=value)", file=sys.stderr)
            continue
        key, _, value = item.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            print(f"warning: ignoring --context with empty key in '{item}'", file=sys.stderr)
            continue
        context[key] = value
    return context


def _print_rendered_prompt(workflow: Workflow) -> None:
    """Print the rendered prompt and any missing-placeholder warnings."""
    print("=" * 72)
    print(f"Workflow: {workflow.name}")
    print("=" * 72)
    print()
    print(workflow.rendered_prompt)
    print()
    print("-" * 72)
    if workflow.missing_placeholders:
        print(
            "Note: the following placeholders had no value supplied and were "
            "left verbatim:"
        )
        for key in workflow.missing_placeholders:
            print(f"  - {{{{{key}}}}}")
        print(
            "Re-run with --input or --context to fill them in."
        )
    else:
        print("All placeholders were filled.")
    print("-" * 72)


def _call_ollama(prompt: str) -> tuple[bool, str]:
    """Call a local Ollama /api/generate endpoint.

    Returns (success, body). On any error, returns (False, reason).
    """
    import requests  # local import to keep startup fast in prompt-only mode

    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {"model": LLM_MODEL, "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.RequestException as exc:
        return False, f"could not reach Ollama at {url}: {exc}"

    if response.status_code != 200:
        return False, f"Ollama returned HTTP {response.status_code}: {response.text.strip()}"

    try:
        data = response.json()
    except ValueError:
        return False, "Ollama returned a non-JSON response"

    body = data.get("response") or data.get("message") or ""
    if not body:
        return False, "Ollama returned an empty response"
    return True, body


def _run_workflow(args: argparse.Namespace) -> int:
    context = _parse_context(args.context or [])

    if args.input:
        context.setdefault("user_input", args.input)

    try:
        workflow = load_workflow(args.workflow)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    rendered = render_workflow(workflow, context)
    _print_rendered_prompt(rendered)

    if ASSISTANT_MODE not in SUPPORTED_MODES:
        print(
            f"\nASSISTANT_MODE='{ASSISTANT_MODE}' is not recognized. "
            f"Supported modes: {sorted(SUPPORTED_MODES)}. "
            "Falling back to prompt-only: no LLM call was made.",
            file=sys.stderr,
        )
        return 0

    if ASSISTANT_MODE == "prompt-only":
        print(
            "\nNo LLM backend configured (ASSISTANT_MODE=prompt-only). "
            "The prompt above is ready to copy into any LLM interface."
        )
        return 0

    if ASSISTANT_MODE == "ollama":
        print(f"\nSending prompt to Ollama at {OLLAMA_BASE_URL} (model={LLM_MODEL})...\n")
        success, body = _call_ollama(rendered.rendered_prompt)
        if not success:
            print(
                "LLM call failed; no model output was generated.\n"
                f"Reason: {body}\n\n"
                "The prompt above is still available for manual use.",
                file=sys.stderr,
            )
            return 1

        print("=" * 72)
        print("LLM response")
        print("=" * 72)
        print()
        print(body)
        print()
        print("-" * 72)
        print("Review the response above before acting on it.")
        print("-" * 72)
        return 0

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assistant",
        description="Context-aware personal AI assistant CLI (PoC).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available workflows and exit.",
    )
    parser.add_argument(
        "--workflow",
        type=str,
        help="Workflow name (without .md) to run.",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Free-form user objective. Passed as {{user_input}}.",
    )
    parser.add_argument(
        "--context",
        action="append",
        help="Structured context field as key=value. Repeatable.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list:
        _print_workflows()
        return 0

    if not args.workflow:
        parser.print_help()
        print("\nerror: --workflow <name> is required (or use --list).", file=sys.stderr)
        return 2

    if not args.input and not args.context:
        print(
            "warning: no --input or --context supplied. "
            "The workflow will render with placeholders left unfilled.",
            file=sys.stderr,
        )

    return _run_workflow(args)


if __name__ == "__main__":
    raise SystemExit(main())