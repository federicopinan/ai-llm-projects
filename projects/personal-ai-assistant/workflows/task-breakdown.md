# Workflow: task-breakdown

## Purpose

Convert a vague goal into an executable list of tasks with explicit definitions of done.

This workflow addresses a specific failure mode: large goals that never start because the next step is unclear.

## Input Format

| Field             | Required | Description                                              |
|-------------------|----------|----------------------------------------------------------|
| `{{user_input}}`  | Yes      | The goal to break down                                    |
| `{{goal_scope}}`  | No       | `small`, `medium`, `large` — affects how granular the breakdown is |
| `{{time_horizon}}`| No       | `today`, `this week`, `this month` — pacing of the plan   |
| `{{constraints}}` | No       | Skill, tool, or access constraints                       |

## Prompt Template

```markdown
You are a task breakdown assistant. Convert the user's goal into a sequenced,
executable plan. Each task must have a definition of done.

# Goal
{{user_input}}

# Goal scope
{{goal_scope}}

# Time horizon
{{time_horizon}}

# Constraints
{{constraints}}

# Your task

Break the goal into phases, then into tasks. Each task must have:
- A concrete action verb in the title
- A definition of done that is testable
- An estimated effort
- Dependencies on other tasks (if any)

# Output format

## Goal restated
(One sentence)

## Phases
### Phase 1: <name>
- [ ] Task 1.1 — <title>
  - Definition of done: ...
  - Effort: ...
  - Dependencies: ...
- [ ] Task 1.2 — ...

### Phase 2: <name>
...

## Start here
(One task the user should begin with right now)
```

## Expected Output Structure

A response containing:

1. **Goal restated** — one sentence
2. **Phases** — sequenced, each with tasks
3. **Per-task fields** — definition of done, effort, dependencies
4. **Start here** — one specific task to begin with

Tasks without a definition of done are treated as failed entries. The user must be able to tell when each task is complete.

## Example

**Input:**

```text
user_input: Build a RAG pipeline over my markdown notes.
goal_scope: medium
time_horizon: this month
constraints: Local-first, Python, no paid APIs.
```

**Expected output (abridged):**

```markdown
## Goal restated
Stand up a local-first RAG pipeline that ingests markdown notes and answers questions
grounded in those notes.

## Phases

### Phase 1: Ingestion
- [ ] Define a markdown loader for the notes directory
  - Definition of done: given a directory, the loader returns a list of documents
    with metadata (path, modified date).
  - Effort: small
  - Dependencies: none
- [ ] Implement chunking strategy
  - Definition of done: chunker produces overlapping chunks of N tokens with source
    path attached.
  - Effort: small
  - Dependencies: loader

### Phase 2: Embedding and storage
- [ ] Pick an embedding model
  - Definition of done: a model runs locally and produces 384/768/etc.-dim vectors.
  - Effort: small
  - Dependencies: none
- [ ] Stand up a local vector store
  - Definition of done: a script inserts chunk embeddings and retrieves top-k by cosine.
  - Effort: medium
  - Dependencies: chunker

### Phase 3: Query layer
- [ ] Wire retrieval into a prompt template
  - Definition of done: a CLI command takes a question, returns an answer with
    cited sources.
  - Effort: medium
  - Dependencies: vector store

## Start here
Phase 1, Task 1: implement the markdown loader. It is the only task with no
dependencies and unblocks every later step.
```

This workflow trades breadth for execution clarity. Each task is small enough that the user can finish it in a single sitting.