# Design Decisions

This document records the trade-offs behind each major choice in the PoC.
The guiding principle is "simple, reproducible, honest": every dependency
must justify its weight, and the project must clearly state what it does
not do.

## Why RAG?

RAG is the right shape for a personal notes assistant because:

- The knowledge base changes constantly. Notes are added, edited, and
  removed daily. Fine-tuning a model on them is impractical.
- Users want answers grounded in what *they* wrote, not in the model's prior
  knowledge. Retrieval keeps the source of truth on disk.
- A RAG pipeline is inspectable: every answer can be traced back to specific
  chunks, which makes evaluation tractable.

For a PoC, RAG is also cheap to build — the same pattern powers production
systems that cost orders of magnitude more.

## Why local-first?

Personal notes are sensitive by default. They contain work projects, health
observations, financial notes, and half-formed ideas. A local-first pipeline
keeps the data on disk and only invokes network endpoints that the user
explicitly enables.

Practical advantages that fall out of this choice:

- No recurring API cost.
- Works offline.
- Reproducible behavior — same inputs, same outputs.
- Easier to audit because every line of code is on the user's machine.

The honest downside is that local embedding models and local LLMs are
usually smaller than the best cloud models, so answer quality may be lower
on hard reasoning tasks.

## Why markdown?

Markdown is the lingua franca of personal knowledge:

- It survives tool changes. Plain `.md` files opened in any editor.
- It diffs cleanly, so notes can live in git.
- It is rich enough for headings, lists, code, and links without the
  complexity of a binary format.

Sticking to markdown means the user's knowledge outlives the application
that wrote it.

## Why ChromaDB?

ChromaDB was chosen for three reasons:

1. **Embedded mode**: `PersistentClient` runs in-process, so the PoC needs
   no separate database server. `docker-compose.yml` is provided as an
   optional alternative for users who want a server.
2. **Batteries included**: the default embedding function is shipped with
   ChromaDB, which removes a class of dependency-conflict problems.
3. **Pythonic API**: short, readable client code, with explicit
   `add`/`query` semantics.

Alternatives considered:

- **FAISS**: faster at scale but requires manual embedding storage and
  metadata bookkeeping. Overkill for a PoC.
- **Qdrant / Weaviate**: production-grade but need a server. Out of scope
  for a "runs in 60 seconds" PoC.
- **LanceDB**: a fine embedded option, but ChromaDB's API is more familiar
  to most readers.

## Why the default embedding function?

`chromadb.utils.embedding_functions.DefaultEmbeddingFunction` uses an ONNX
build of `all-MiniLM-L6-v2`. It is small (~80 MB), runs on CPU, and avoids
the heavy PyTorch dependency that `sentence-transformers` brings in.

For a PoC, "good enough and zero install drama" beats "slightly better and
hundreds of megabytes". If a user needs higher-quality embeddings, swapping
the embedding function in `src/ingest.py` and `src/query.py` is a one-line
change.

## Why optional Ollama?

Ollama lets users run open-source LLMs locally with one command
(`ollama pull llama3.1` + `ollama serve`). It exposes a tiny HTTP API, so
the integration uses `urllib.request` from the Python standard library —
no extra dependency.

The LLM is **optional** because:

- A RAG PoC is valuable on its own: retrieval + grounded extract is already
  useful for inspecting what the system found.
- Mandating an LLM doubles the install burden and excludes users who only
  want the retrieval half.
- Keeping the LLM call behind a single function (`call_ollama` in
  `src/query.py`) makes it trivial to disable or replace.

If Ollama is unreachable, the CLI fails gracefully and falls back to an
extractive summary. This is a feature, not a bug — the PoC remains
useful offline.

## Why a simple paragraph chunker?

The chunker in `src/ingest.py` splits on blank lines and packs paragraphs
greedily with overlap. Compared to dedicated splitters
(`langchain.text_splitter`, `semantic-chunker`), it is:

- ~40 lines, no extra dependency.
- Easy to reason about and tune with two env vars (`CHUNK_SIZE`,
  `CHUNK_OVERLAP`).
- Predictable: identical input produces identical chunks.

It is also clearly *not* state-of-the-art: it does not respect document
structure beyond paragraphs, and it does not adapt chunk boundaries to the
embedding model. For the PoC this is a fair price.

## Why are secrets handled this way?

There are no secrets in this PoC. The `.env.example` file documents every
variable, with safe defaults. Real secrets would belong in `.env`, which is
already excluded by `.gitignore`.

## What the PoC is not trying to be

This is not a production system. There is no auth, no encryption at rest,
no incremental ingest, no reranker, no observability, no automated
evaluation harness. See `limitations.md` for the honest list.