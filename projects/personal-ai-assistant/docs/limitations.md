# Limitations

This document is honest about what the Personal AI Assistant PoC cannot do.

If a reader evaluates this project for production use, this is the section to read first.

## No persistent memory

The assistant has no memory between invocations.

- Each CLI run is stateless.
- Context is provided fresh on every call.
- There is no user profile, no preference store, no history of past workflows.

**Consequence:** the user must repeat context (priorities, constraints, energy level) every time. This is intentional — see [`design-decisions.md`](design-decisions.md) — but it is a real limitation for users who would expect the assistant to "know them" over time.

## No calendar integration

The assistant cannot read or write calendar events.

- It cannot see existing meetings.
- It cannot create calendar blocks.
- It cannot detect scheduling conflicts.

**Consequence:** daily-planning output is best-effort. The user must reconcile it with their actual calendar manually.

## No email integration

The assistant cannot read, send, or draft email.

- It cannot summarize an inbox.
- It cannot propose replies.
- It cannot detect action items buried in email threads.

**Consequence:** research-assistant and decision-support workflows that depend on real-world correspondence must be fed that correspondence as text. The assistant does not pull it.

## No task-system integration

The assistant cannot create, update, or close tasks in any external system.

- No Notion, Todoist, Linear, GitHub Issues, or similar integrations.
- Output is plain text the user can copy elsewhere.

**Consequence:** task-breakdown output requires manual transcription into whatever task system the user actually uses.

## No authentication

The CLI has no concept of users.

- No login flow.
- No per-user config.
- No access control.

**Consequence:** this PoC is intended to run locally on a single user's machine. It is not safe to expose as a network service.

## No autonomous execution

The assistant never takes an action on the user's behalf.

- It does not call APIs other than the optional Ollama backend.
- It does not write to the filesystem except via stdout.
- It does not modify any external state.

**Consequence:** every workflow output is advisory. The user is responsible for acting on it.

## Output requires human review

The assistant does not validate its outputs against ground truth.

- It does not check facts against external sources.
- It does not verify the feasibility of proposed schedules.
- It does not guarantee that recommended options actually meet the stated criteria.

**Consequence:** every output should be treated as a draft for human review. This is documented in [`design-decisions.md`](design-decisions.md) but cannot be overstated.

## No prompt optimization

The workflow templates are static.

- There is no automatic prompt tuning.
- There is no evaluation suite that scores outputs.
- There is no A/B testing of template variants.

**Consequence:** improving a workflow means editing the markdown file manually. This is a feature, not a bug, for a PoC — but it limits scalability.

## LLM backend is best-effort

The optional Ollama integration is intentionally minimal.

- No streaming responses.
- No retry logic beyond a single connection attempt.
- No token counting or context-window enforcement.
- No fallback to a cloud provider.

**Consequence:** if Ollama is unreachable, the assistant prints the prompt and explains why no LLM was invoked. The user must diagnose the connection themselves.

## Limited workflow catalog

Four workflows ship with the PoC.

- Daily planning
- Research summarization
- Task breakdown
- Decision support

**Consequence:** tasks outside this catalog require either extending the PoC with new workflow files or falling back to a generic chat interface. Adding a workflow is documented in [`workflows.md`](workflows.md) and requires only a new markdown file.

## What this PoC is not

This project is not:

- A replacement for a real personal assistant
- A multi-tenant SaaS
- A production-ready agent framework
- A model evaluation harness

It is a **prompt-layer artifact** that demonstrates reusable structure for personal AI workflows. Treat it accordingly.