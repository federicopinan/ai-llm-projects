# Workflow: decision-support

## Purpose

Compare options using pros, cons, risks, trade-offs, and a recommendation.

This workflow is designed to surface hidden trade-offs before a decision is made, and to require the model to recommend rather than hedge behind "it depends".

## Input Format

| Field           | Required | Description                                              |
|-----------------|----------|----------------------------------------------------------|
| `{{user_input}}`| Yes      | The decision to be made                                  |
| `{{options}}`   | Yes      | Candidate options (list of 2-4 items)                    |
| `{{criteria}}`  | Yes      | What matters most in the decision                        |
| `{{constraints}}`| No      | Non-negotiables or hard limits                           |

## Prompt Template

```markdown
You are a decision support assistant. The user is choosing between options and needs
a structured comparison, not a vague summary.

# Decision
{{user_input}}

# Options
{{options}}

# Criteria (in order of importance)
{{criteria}}

# Constraints
{{constraints}}

# Your task

Compare the options honestly, including their downsides. Make a recommendation with
explicit reasoning. The user must be able to disagree with the recommendation and
still find the analysis useful.

# Output format

## Options restated
- Option A: ...
- Option B: ...
- ...

## Comparison matrix
| Criterion | Option A | Option B | ... |

## Pros and cons

### Option A
- Pros: ...
- Cons: ...
- Risks: ...

### Option B
...

## Trade-off summary
(1-3 sentences capturing the central trade-off the user must accept)

## Recommendation
**Pick Option X** because...
- (Reason 1, tied to a criterion)
- (Reason 2, tied to a criterion)

## Reversibility
- Can this decision be undone cheaply? If not, what is the cost of reversal?
```

## Expected Output Structure

A response containing:

1. **Options restated** — concrete and distinct
2. **Comparison matrix** — option × criterion
3. **Pros, cons, risks per option** — at least 2 of each where possible
4. **Trade-off summary** — 1-3 sentences
5. **Recommendation** — explicit pick with reasoning tied to criteria
6. **Reversibility note** — can this be undone, and at what cost

The recommendation is mandatory. A workflow run without a recommendation is treated as incomplete.

## Example

**Input:**

```text
user_input: I need to choose a vector database for my local RAG PoC.
options: ChromaDB, FAISS, pgvector
criteria: local-first, ease of setup, retrieval quality
constraints: must run offline, Python-friendly
```

**Expected output (abridged):**

```markdown
## Options restated
- Option A: ChromaDB — embedded vector DB with Python-native API.
- Option B: FAISS — library for similarity search, no built-in persistence layer.
- Option C: pgvector — Postgres extension for vector search.

## Comparison matrix
| Criterion           | ChromaDB       | FAISS          | pgvector      |
|---------------------|----------------|----------------|---------------|
| Local-first         | Yes            | Yes            | Yes (with PG) |
| Ease of setup       | High           | Medium         | Medium        |
| Retrieval quality   | Good           | Excellent      | Good          |

## Pros and cons

### ChromaDB
- Pros: batteries-included, persistent storage, easy metadata filtering.
- Cons: younger ecosystem, less tunable than FAISS.
- Risks: future API churn.

### FAISS
- Pros: battle-tested, very fast, large index types.
- Cons: no persistence out of the box; you wire your own.
- Risks: more glue code means more places to break.

### pgvector
- Pros: SQL composability, single system of record.
- Cons: requires running Postgres; not pure-local for some users.
- Risks: scaling past ~1M vectors needs care.

## Trade-off summary
ChromaDB trades some retrieval quality and tunability for the simplest end-to-end
setup, which is what a PoC benefits from. FAISS wins on raw quality at the cost of
more wiring.

## Recommendation
**Pick ChromaDB** for this PoC.

- Reason 1 (ease of setup): ChromaDB lets the user focus on the RAG pipeline rather
  than on infrastructure. The PoC's value is in the pipeline, not the vector store.
- Reason 2 (local-first): ChromaDB runs fully embedded, which matches the constraint.
- Reason 3 (retrieval quality): for the document volume of a personal notes PoC,
  ChromaDB's quality is sufficient.

## Reversibility
This decision is reversible with moderate effort. Migration to FAISS or pgvector is
a one-time reindex and rewrite of the retriever module. Cost of reversal is acceptable.
```

If the decision is irreversible, the recommendation must explicitly note that and justify a higher standard of evidence.