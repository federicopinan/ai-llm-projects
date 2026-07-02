# Workflow: research-assistant

## Purpose

Summarize technical material without inventing unsupported claims.

This workflow enforces a strict discipline: every claim in the summary must be tagged with the model's confidence, and unverified claims must be flagged rather than polished into apparent certainty.

## Input Format

| Field           | Required | Description                                              |
|-----------------|----------|----------------------------------------------------------|
| `{{user_input}}`| Yes      | The source material or topic to summarize                |
| `{{source_type}}`| No      | `paper`, `notes`, `article`, `transcript`, `topic`       |
| `{{audience}}`  | No       | Who the summary is for, e.g. `self-study`, `team brief`  |
| `{{depth}}`     | No       | `quick`, `standard`, `deep`                              |

## Prompt Template

```markdown
You are a research summarization assistant. Your job is to summarize the provided
material without inventing claims the source does not support.

# Source material or topic
{{user_input}}

# Source type
{{source_type}}

# Audience
{{audience}}

# Desired depth
{{depth}}

# Your task

Produce a summary that separates what the source actually says from what is uncertain
or extrapolated. Do not smooth over uncertainty.

# Output format

## Headline
(2-3 sentences capturing the main point)

## Key claims
- Claim 1 — confidence: [supported | partial | uncertain]
- Claim 2 — confidence: [supported | partial | uncertain]
- ...

## Open questions
- (What the source does not answer)

## Caveats
- (Limitations of the source, missing context, contradictions)
```

## Expected Output Structure

A response containing:

1. **Headline** — 2-3 sentence summary
2. **Key claims** — each tagged `supported`, `partial`, or `uncertain`
3. **Open questions** — what is not answered
4. **Caveats** — source limitations, contradictions, missing context

The `confidence` tag is mandatory. A summary without confidence tags is treated as a failed workflow run.

## Example

**Input:**

```text
user_input: RAG systems combine retrieval with generation to ground LLM outputs in
            external knowledge. Common failure modes include stale retrievals, chunk
            boundary issues, and hallucination despite grounding.
source_type: notes
audience: self-study
depth: standard
```

**Expected output (abridged):**

```markdown
## Headline
RAG systems pair an information retrieval step with an LLM generator so that the
generator's response is grounded in retrieved documents rather than only the model's
parametric memory. The approach reduces but does not eliminate hallucination.

## Key claims
- Retrieval grounding reduces hallucination relative to ungrounded generation — confidence: supported
- Stale retrieval corpora cause outdated answers — confidence: supported
- Chunk boundary splits degrade retrieval precision — confidence: partial
- Hallucination disappears when retrieval is good — confidence: uncertain

## Open questions
- How is retrieval quality measured in practice?
- What chunking strategy fits which document type?

## Caveats
- The source is informal notes, not a peer-reviewed survey.
- Claims about "eliminating" hallucination are likely overstated.
```

This workflow is deliberately conservative. It is the opposite of a confidence-laundering summary.