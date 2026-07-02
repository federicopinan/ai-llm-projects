# Sample Output

This file shows a realistic structured output produced by the
`daily-planning` workflow for the input documented in
[`sample-prompt.md`](sample-prompt.md).

It is a synthetic example for portfolio purposes. It is not the output of
a specific model run; it illustrates the shape and depth of the
structured response the workflow is designed to elicit.

The output below is what a user could reasonably expect when sending the
rendered prompt to a capable instruction-following model. The actual
content would vary across models and runs.

---

## Workflow: daily-planning

### User objective

The user has 3 hours today. They need to review SIEM alerts, document
their RAG project, train, and study one MITRE ATT&CK technique.

### Available time

3 hours

### Priorities

1. SIEM alert review
2. RAG project documentation
3. Training
4. MITRE ATT&CK study

### Energy level

Medium

### Constraints

No meetings today.

---

## Schedule

| Time block | Task                          | Type      |
|------------|-------------------------------|-----------|
| 0:00 - 0:30 | SIEM alert review             | shallow   |
| 0:30 - 1:15 | RAG project documentation     | deep      |
| 1:15 - 1:30 | Break                         | recovery  |
| 1:30 - 2:00 | MITRE ATT&CK technique study  | deep      |
| 2:00 - 2:30 | Training                      | shallow   |
| 2:30 - 3:00 | Buffer + end-of-day review    | buffer    |

## Sequencing rationale

- SIEM review goes first because it is time-sensitive, requires triage
  judgment, and serves as a natural warm-up before deep work.
- RAG documentation gets the first deep-work block while energy is
  highest after the warm-up.
- MITRE ATT&CK study takes the second deep-work slot; one technique is
  realistic for 30 minutes of focused study.
- Training is placed late because it is low-stakes and the user can
  reschedule if focus collapses.
- The last 30 minutes are reserved as buffer. This is intentional: the
  schedule should absorb overruns without cascading.

## Trade-offs

- **Training session is short.** A full session would require dropping
  another priority; the user can move training to a low-friction slot
  tomorrow.
- **MITRE study is limited to one technique.** A full tactic would
  require 90 minutes minimum and is not realistic given the time
  budget.
- **Buffer is treated as mandatory.** The schedule assumes at least
  one priority will overrun.

## End-of-day review

1. Which task produced the most value per minute spent?
2. Which deferred item should move to tomorrow's plan, and why?
3. What interrupted focus today, and what could reduce that interruption
   tomorrow?

---

## Notes for reviewers

- The schedule fits the 3-hour budget exactly.
- Each block has a clear type (shallow / deep / recovery / buffer).
- The trade-offs section is explicit about what was sacrificed.
- The review section gives the user a small, reusable reflection
  ritual.

This is the shape of output the workflow is designed to produce. A real
LLM run may phrase things differently but should preserve:

- Time-blocked structure
- Explicit sequencing rationale
- Honest trade-off disclosure
- A short end-of-day reflection step