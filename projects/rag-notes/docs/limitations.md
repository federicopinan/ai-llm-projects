# Limitations

This document is intentionally frank. The PoC has narrow scope, and treating
it as more than that would mislead the next reader.

## Not production-ready

- No authentication or authorization. Anyone with shell access can query the
  index.
- No multi-user support. The Chroma DB and the notes directory are owned by
  a single user account.
- No concurrency guarantees. Two simultaneous `ingest.py` runs may race on
  the same Chroma directory.
- No migration story. The collection is rebuilt from scratch on every
  ingest, so any direct edits to the Chroma DB are wiped on the next run.

## Storage and privacy

- **No encryption at rest.** Notes, chunks, and embeddings sit on disk in
  plaintext (markdown) or in ChromaDB's native format. If the disk is
  compromised, the data is exposed.
- **No key management.** There is no way to require a passphrase to read the
  index.
- **Vector store is not anonymized.** Embeddings leak information about the
  source text; in some threat models, embedding inversion is a concern.
- **No data retention policy.** There is no automatic pruning or expiry.

## Evaluation

- **No automated eval.** All checks are manual (see `evaluation.md`).
- **No ground-truth dataset.** The shipped notes are synthetic; an honest
  evaluation requires real notes and real questions.
- **No regression tracking.** Re-running the pipeline does not produce a
  report; changes in retrieval quality are invisible without manual
  comparison.
- **No baseline comparison.** There is no "BM25-only" or "no-reranker"
  branch to compare against.

## Retrieval

- **Single retriever.** Cosine similarity over `all-MiniLM-L6-v2`. No
  hybrid search (BM25 + dense), no reranker, no cross-encoder.
- **No metadata filtering.** A query cannot be scoped to a single note or
  tag.
- **No incremental ingest.** Edits to notes do not update the index until
  `ingest.py` is run again.
- **Chunking is heuristic.** Paragraph-based, no structural awareness of
  markdown headings, code blocks, or tables.
- **No query rewriting or expansion.** The raw user question is embedded
  directly.

## Generation

- **LLM is optional and best-effort.** When Ollama is unreachable, the CLI
  falls back to an extractive summary. There is no retry, no queue, no
  timeout that surfaces to the user beyond a fallback message.
- **No streaming.** Ollama is called with `stream: false`, so the user sees
  the full answer at once.
- **Prompt is fixed.** There is no per-query prompt template, no system
  message, no tool use. The prompt lives in `src/query.py` and is meant to
  be edited by hand.
- **No answer validation.** Generated text is printed as-is. There is no
  citation-checking, no hallucination filter, no length cap.

## Operations

- **No logging.** The CLI prints to stdout. There is no log file, no
  structured logging, no metrics.
- **No telemetry.** Nothing leaves the machine except an optional Ollama
  call.
- **No CI.** There are no GitHub Actions, no linters configured for Python,
  no test suite.
- **No packaging.** The project is not published as a wheel. It runs from
  source with a virtualenv.

## Content

- **Synthetic notes only.** The shipped corpus is three hand-written
  notes on local-first AI, AI agents, and personal knowledge management.
  It is not representative of any real user's notes.
- **English only.** The pipeline does not handle multilingual notes or
  multilingual queries.
- **No code-aware chunking.** A note with long code blocks will have those
  blocks split mid-function if they exceed `CHUNK_SIZE`.

## When *not* to use this PoC

- Anywhere you would expose it to other users (no auth, no isolation).
- On notes that must remain encrypted at rest.
- For high-stakes reasoning where a wrong answer has real consequences.
- As a substitute for a properly evaluated retrieval system with a real
  test set.

For those cases, build a real product. This PoC is a learning artifact and
a starting point — not a finished system.