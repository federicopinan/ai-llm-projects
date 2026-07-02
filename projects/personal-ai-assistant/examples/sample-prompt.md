# Sample Prompt

This file shows what a realistic user input looks like for the
`daily-planning` workflow. It is the same input that the assistant's
README uses as a quick example.

## Command

```bash
python src/assistant.py \
  --workflow daily-planning \
  --input "I have 3 hours today. I need to review SIEM alerts, document my RAG project, train, and study one MITRE ATT&CK technique."
```

## User objective (free-form)

> I have 3 hours today. I need to review SIEM alerts, document my RAG project, train, and study one MITRE ATT&CK technique.

## Structured context (alternative invocation)

```bash
python src/assistant.py \
  --workflow daily-planning \
  --context available_time=3h \
  --context priorities="SIEM alert review, RAG project documentation, training, MITRE ATT&CK study" \
  --context energy_level=medium \
  --context constraints="No meetings today"
```

## Expected CLI behavior

1. Load `workflows/daily-planning.md`.
2. Extract the prompt template.
3. Substitute the placeholders with the user input and structured fields.
4. Print the rendered prompt to stdout.
5. Because `ASSISTANT_MODE=prompt-only` by default, the CLI stops here and
   explains that no LLM backend is configured.

The user can then:

- Copy the rendered prompt into any chat interface.
- Pipe it to a file: `... --input "..." > today.md`.
- Switch to `ASSISTANT_MODE=ollama` in `.env` and re-run to send it to a
  local model.

## Why this example

The scenario combines four different work modes (security operations,
software documentation, physical training, structured study). It
exercises the planner's ability to sequence deep and shallow work, leave
a buffer, and make explicit trade-offs.