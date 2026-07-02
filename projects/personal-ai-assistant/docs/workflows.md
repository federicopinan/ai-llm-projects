# Workflows

This document summarizes each workflow shipped with the assistant and when to use it.

Each workflow is defined as a markdown file under [`../workflows/`](../workflows/). The CLI loads them by name.

## `daily-planning`

**Purpose:** Turn available time and a list of priorities into a realistic daily execution plan with time blocks, sequencing, and a short review step.

**Use it when:**

- You have a finite block of time and multiple competing tasks.
- You need to make trade-offs between deep work, shallow work, and recovery.
- You want a schedule you can actually follow, not a motivational poster.

**Input:**

- `{{user_input}}` — free-form description of the day
- `{{available_time}}` — total time available (e.g. `3h`, `90m`, `full day`)
- `{{priorities}}` — explicit list of tasks to fit in
- `{{energy_level}}` — `high`, `medium`, `low`
- `{{constraints}}` — any hard constraints (meetings, deadlines, dependencies)

**Output shape:**

- Time blocks with start/end and task
- Sequencing rationale (why this order)
- Buffer and recovery slots
- End-of-day review prompt

See [`../workflows/daily-planning.md`](../workflows/daily-planning.md).

## `research-assistant`

**Purpose:** Summarize technical material without inventing unsupported claims.

**Use it when:**

- You have notes, an article, or a transcript and need a grounded summary.
- You want the model to flag uncertainty instead of papering over it.
- You are studying a topic and need to know what is solid and what is speculation.

**Input:**

- `{{user_input}}` — the source material or topic
- `{{source_type}}` — `paper`, `notes`, `article`, `transcript`, `topic`
- `{{audience}}` — who the summary is for (e.g. `self-study`, `team brief`)
- `{{depth}}` — `quick`, `standard`, `deep`

**Output shape:**

- Headline summary (2-3 sentences)
- Key claims, each tagged as `supported`, `partial`, or `uncertain`
- Open questions
- Citations or pointers to the source material

See [`../workflows/research-assistant.md`](../workflows/research-assistant.md).

## `task-breakdown`

**Purpose:** Convert a vague goal into an executable list of tasks with clear done-criteria.

**Use it when:**

- You have a goal that is too large to start ("build a RAG pipeline").
- You keep procrastinating because the next step is unclear.
- You want each task to have a definition of done so progress is visible.

**Input:**

- `{{user_input}}` — the goal to break down
- `{{goal_scope}}` — `small`, `medium`, `large`
- `{{time_horizon}}` — `today`, `this week`, `this month`
- `{{constraints}}` — skill, tool, or access constraints

**Output shape:**

- Goal restated in one sentence
- Sequenced phases
- Concrete tasks per phase, each with:
  - Definition of done
  - Estimated effort
  - Dependencies on other tasks
- First task to start with

See [`../workflows/task-breakdown.md`](../workflows/task-breakdown.md).

## `decision-support`

**Purpose:** Compare options using pros, cons, risks, trade-offs, and a recommendation.

**Use it when:**

- You are choosing between 2-4 options and want a structured comparison.
- You need to surface hidden trade-offs before committing.
- You want the model to recommend, but with explicit reasons you can audit.

**Input:**

- `{{user_input}}` — the decision to make
- `{{options}}` — list of candidate options
- `{{criteria}}` — what matters most in the decision
- `{{constraints}}` — non-negotiables

**Output shape:**

- Options restated
- Comparison matrix: option × criterion
- Pros, cons, risks per option
- Trade-off summary
- Recommendation with explicit reasoning
- Reversibility note (can you undo this decision?)

See [`../workflows/decision-support.md`](../workflows/decision-support.md).

## Choosing the right workflow

If you are unsure which workflow to use:

| Symptom                                            | Likely workflow      |
|----------------------------------------------------|----------------------|
| "I have N hours and N+3 things to do"              | `daily-planning`     |
| "I read this thing, summarize it"                  | `research-assistant` |
| "I want to start X but it's huge"                  | `task-breakdown`     |
| "Should I do A or B?"                              | `decision-support`   |

These workflows are not mutually exclusive. A common sequence:

1. `task-breakdown` a large goal into phases.
2. `daily-planning` each day from that breakdown.
3. `research-assistant` when you hit a knowledge gap.
4. `decision-support` when a phase requires a choice.