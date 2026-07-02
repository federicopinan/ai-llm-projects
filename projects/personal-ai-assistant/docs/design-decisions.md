# Design Decisions

This document explains the non-obvious design choices behind the Personal AI Assistant PoC.

Each decision is stated, then justified with the constraint or trade-off that produced it.

## 1. Why workflow-based, not chat-based?

A chat interface optimizes for free-form conversation. That is the wrong shape for recurring personal tasks.

When the user says "help me plan my day" for the hundredth time, they do not want a fresh conversation. They want the **same structured workflow** they used the first time, refined over time.

A workflow-based assistant:

- Encodes the structure of the task in a versionable artifact (markdown file).
- Makes the prompt reproducible.
- Lets the user improve the prompt without touching code.

The trade-off is reduced flexibility: the user picks from a finite set of workflows. For a PoC focused on daily planning, research, task breakdown, and decision support, that is the right trade-off.

## 2. Why markdown prompts?

Markdown is the lowest-friction authoring format for prompts that already contain structure.

Prompts in this PoC are not single sentences. They contain sections, placeholders, and expected output shapes. Markdown supports all of that natively, renders well in any text editor, and diffs cleanly in git.

A DSL or YAML-based prompt format would add tooling requirements without adding expressive power for this use case. Plain markdown wins on:

- Zero learning curve
- Direct rendering in editors and PR reviews
- No build step

## 3. Why context-aware prompting?

A prompt without context produces generic output.

`"Plan my day"` → generic advice.
`"Plan my 3-hour day focused on SIEM review, RAG docs, training, and one MITRE ATT&CK technique"` → actionable plan.

The assistant injects user-supplied context into the prompt template before sending it to the LLM. This is the simplest possible form of personalization and the most reliable: the user is the source of truth.

The PoC does not invent context. It does not infer priorities from past behavior. It does not mine the user's calendar or email. It only uses what the user explicitly provides in the current invocation.

## 4. Why no full autonomy by default?

Autonomous agents are powerful and dangerous in roughly equal measure.

A fully autonomous personal assistant can:

- Send emails the user did not intend to send
- Create calendar events at the wrong time
- Spend money on a wrong purchase
- Make commitments the user cannot keep

For a PoC — and arguably for any personal assistant until models are demonstrably more reliable — the safer default is **advisory mode**: the assistant produces output, the human reviews it, the human acts on it.

This is enforced architecturally: the CLI has no side effects other than printing to stdout and (optionally) calling an LLM backend. There is no API for the assistant to act on the world.

## 5. Why does human review matter?

LLMs hallucinate, omit, misweight, and confidently state incorrect facts.

This is not a bug to be patched in a future version. It is a current property of the technology. Any system that removes the human from the loop inherits that property directly.

The PoC is designed so that every output is **reviewable**:

- Prompt-only mode prints the prompt for inspection before any LLM call.
- LLM mode prints both the prompt and the response.
- Outputs are structured but not validated against ground truth.

If the user chooses to skip review, that is the user's choice. The assistant does not pretend review is unnecessary.

## 6. Why a CLI, not a web UI?

A CLI is the smallest possible interface that still demonstrates the architecture end-to-end.

It avoids:

- Web framework selection
- Frontend state management
- Authentication and session handling
- Deployment complexity

And it preserves:

- Direct stdout inspection of the generated prompt
- Pipe-friendly output for shell composition
- Easy version control of every invocation (via shell history)

A web UI is a future improvement, not a current requirement.

## 7. Why Ollama, not OpenAI or Anthropic?

The local-first direction is consistent with the privacy stance in [`../README.md`](../README.md).

Ollama provides:

- A single HTTP endpoint at `localhost:11434`
- No API keys to manage
- A growing library of open-source models
- Easy fallback: if Ollama is not running, the CLI falls back to prompt-only mode

Cloud providers remain a valid future addition, but they would change the privacy profile of the assistant and were intentionally deferred.

## 8. Why no framework (LangChain, LlamaIndex, etc.)?

Frameworks add abstractions. For a PoC whose value is the **visible prompt layer**, abstractions are liabilities:

- They hide where the prompt goes.
- They introduce silent retries, callbacks, and tool invocations.
- They make it harder to explain the system in a portfolio setting.

The PoC uses only `requests` (for the optional LLM call) and `python-dotenv` (for configuration). Both are replaceable in a few lines if needed.

## 9. Why four workflows, not one generic workflow?

Four workflows are enough to demonstrate the pattern without becoming a kitchen sink.

Each workflow solves a real recurring personal task with a distinct prompt shape:

| Workflow        | Prompt shape                              |
|-----------------|-------------------------------------------|
| Daily planning  | Time-bucketed schedule with priorities    |
| Research        | Source-grounded summary with citations    |
| Task breakdown  | Hierarchical action list with criteria    |
| Decision support| Comparative analysis with trade-offs      |

A single generic "help me think" workflow would dilute the point. Specificity is the design.