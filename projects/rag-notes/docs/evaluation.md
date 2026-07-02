# Evaluation

This PoC is evaluated **manually**. There is no automated eval harness, no
test set, and no scoring script. The reason is honest scope: building a
realistic evaluation for a personal-notes RAG requires a real personal
notes corpus, and the PoC explicitly ships synthetic data only.

This document defines the manual checks that the project should pass.

## What we are evaluating

The pipeline has two stages and both are inspected:

1. **Retrieval**: do the top-k chunks actually answer the question?
2. **Answer generation** (when an LLM is configured): is the generated text
   faithful to the retrieved context?

## Criteria

### 1. Relevance of retrieved chunks

For each question, at least one of the top `TOP_K` chunks should:

- Come from a source file that plausibly contains the answer.
- Contain the key concepts mentioned in the question (paraphrased or
  literal).

Failure mode: irrelevant chunks dominate the top results. Symptom: every
retrieved chunk is from the wrong note, or covers the wrong section of the
right note.

How to check: run a query, inspect the printed chunks. Their `source` and
`chunk_index` should match the expected note and section for the question.

### 2. Groundedness

If an LLM is configured, the generated answer must only use information
present in the retrieved chunks. A grounded answer:

- Cites the source filename in brackets (the prompt instructs the model to
  do so, but compliance is the model's responsibility).
- Does not introduce facts that are absent from the chunks.
- Refuses to answer when the chunks do not contain the answer.

Failure mode: the model "fills in" with prior knowledge that is not in the
user's notes. Symptom: claims that cannot be traced to any retrieved chunk.

How to check: pick a question whose answer is in the chunks, then read the
generated answer side by side with the chunks. Every claim should map to a
chunk.

### 3. Hallucination avoidance

This is the strict form of groundedness: the answer should never state
something that contradicts the retrieved chunks. Especially watch for:

- Wrong numbers, names, or dates.
- Confident answers when the chunks only contain vague hints.
- "I cannot find this in your notes" — desirable when the answer truly is
  not there.

How to check: ask a question whose answer is *not* in the notes. The model
should say so. If it produces a confident answer, the prompt template or
the temperature may need tuning.

### 4. Latency

Targets for a typical laptop:

- `ingest.py` on the shipped sample notes: under 30 seconds.
- `query.py` without an LLM: under 2 seconds end-to-end.
- `query.py` with Ollama on CPU: under 15 seconds for a short prompt.
- `query.py` with Ollama on GPU: under 5 seconds.

How to check: time the commands with `time python src/ingest.py` and
`time python src/query.py "..."`.

### 5. Reproducibility

The pipeline must be reproducible:

- `python src/ingest.py` produces the same Chroma DB state given the same
  notes.
- `python src/query.py "..."` returns the same top-k chunks and the same
  distances on every run.
- LLM answers are not required to be byte-identical, but they should be
  semantically stable across runs (set `temperature: 0.2` in the prompt
  payload).

How to check: run ingest twice with no note changes; delete
`./chroma_db`; re-ingest; verify the query output is unchanged.

## Suggested manual test set

Use the four queries in `examples/sample-query.md`. For each one, record:

| Query | Top source file | Top chunk index | Expected coverage |
|-------|------------------|------------------|--------------------|
| Benefits of local-first AI | local-first-ai.md | 1, 2 | Core principles, Practical benefits |
| Main parts of an AI agent | ai-agents.md | 1, 2 | Anatomy, Common patterns |
| Linking over folders | personal-knowledge.md | 1, 4 | Linking, Retrieval |
| Agents + PKM | ai-agents.md + personal-knowledge.md | 3, 4 | Why agents matter for notes, Retrieval |

A passing run covers the expected notes and chunks.

## What this evaluation is *not*

- It is not a benchmark. There are no aggregate scores.
- It is not statistical. Sample size is three notes by design.
- It does not compare embedding models, chunk sizes, or retrievers.
- It does not measure answer quality against a gold standard.

Those are interesting follow-ups, but they would require a real evaluation
corpus, which is out of scope for a PoC that ships with synthetic notes.