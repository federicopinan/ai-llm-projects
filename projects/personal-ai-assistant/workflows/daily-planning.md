# Workflow: daily-planning

## Purpose

Turn available time and a list of priorities into a realistic, time-blocked daily execution plan.

This workflow is designed for days where the user has more tasks than time and needs to make honest trade-offs.

## Input Format

| Field             | Required | Description                                              |
|-------------------|----------|----------------------------------------------------------|
| `{{user_input}}`  | Yes      | Free-form description of the day, constraints, intent    |
| `{{available_time}}` | Yes   | Total time available, e.g. `3h`, `90m`, `full day`       |
| `{{priorities}}`  | Yes      | Explicit list of tasks to fit into the available time    |
| `{{energy_level}}`| No       | `high`, `medium`, `low` — used to sequence deep work     |
| `{{constraints}}` | No       | Hard constraints (meetings, deadlines, dependencies)    |

## Prompt Template

```markdown
You are a personal planning assistant. The user needs a realistic daily execution plan,
not an aspirational one.

# User objective
{{user_input}}

# Available time
{{available_time}}

# Priorities (in user's own order)
{{priorities}}

# Energy level
{{energy_level}}

# Constraints
{{constraints}}

# Your task

Produce a time-blocked plan that fits the available time, sequences work by energy level,
and explicitly leaves a buffer. Prefer realistic allocations over an optimistic schedule.

# Output format

## Schedule
| Time block | Task | Type (deep / shallow / recovery) |

## Sequencing rationale
- (Explain why this order)

## Trade-offs
- (What was dropped or deferred, and why)

## End-of-day review
- (3 questions the user should answer before closing the day)
```

## Expected Output Structure

A response containing:

1. **Schedule table** — time-blocked, in user-friendly units
2. **Sequencing rationale** — 2-5 bullets explaining the order
3. **Trade-offs** — explicit list of what was deferred
4. **End-of-day review** — 3 reflective questions

The output must fit the available time. If priorities exceed available time, the assistant must drop or defer tasks explicitly rather than compress them.

## Example

**Input:**

```text
user_input: I have 3 hours today. I need to review SIEM alerts, document my RAG project,
            train, and study one MITRE ATT&CK technique.
available_time: 3h
priorities: SIEM alert review, RAG project documentation, training, MITRE ATT&CK study
energy_level: medium
constraints: No meetings today
```

**Expected output (abridged):**

```markdown
## Schedule
| Time block | Task                          | Type     |
|------------|-------------------------------|----------|
| 0:00-0:30  | SIEM alert review             | shallow  |
| 0:30-1:15  | RAG project documentation     | deep     |
| 1:15-1:30  | Break                         | recovery |
| 1:30-2:00  | MITRE ATT&CK technique study  | deep     |
| 2:00-2:30  | Training                      | shallow  |
| 2:30-3:00  | Buffer + review               | buffer   |

## Sequencing rationale
- SIEM review first because it is time-sensitive and shallow.
- RAG documentation during the energy peak after a warm-up.
- MITRE study in the second deep-work slot.
- Training last because it is the lowest-stakes task.

## Trade-offs
- Training session shortened to 30 minutes.
- MITRE study covers one technique, not a full tactic.

## End-of-day review
- Which task produced the most value per minute?
- Which deferred item should move to tomorrow's plan?
- What blocked focus, and how can it be reduced tomorrow?
```

A full sample output is in [`../examples/sample-output.md`](../examples/sample-output.md).