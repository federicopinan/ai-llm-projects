# RAG Pipeline for Private Notes

A local-first Retrieval-Augmented Generation proof of concept for querying
private markdown notes using embeddings, vector search, and an optional
local LLM response layer.

> **Status: PoC / Experimental.**
> Synthetic notes only. No real personal data is included. No auth. No
> encryption at rest. See `docs/limitations.md` for the honest scope.

---

## Overview

This project demonstrates a reproducible RAG workflow over a personal
markdown notes collection:

1. Markdown notes are loaded, chunked, embedded, and stored in a local
   ChromaDB vector database.
2. A user asks a question from the CLI.
3. The retriever fetches the most relevant chunks.
4. If a local LLM (Ollama) is available, the chunks are passed as context
   for a grounded answer. If not, the CLI prints the retrieved chunks and a
   simple extractive summary.

The whole pipeline runs on a laptop. Notes, embeddings, and the optional
LLM call all stay on the user's machine.

## Problem

Personal knowledge is fragmented across notes, documents, chats, bookmarks,
and research files. Traditional keyword search is limited when the user
does not remember the exact wording. This PoC tests whether semantic
search and LLM-based answer generation can improve retrieval over a
private knowledge base — without sending the data to a third party.

## Goals

- Ingest markdown notes from a local directory.
- Split documents into searchable chunks.
- Generate embeddings locally.
- Store vectors in a local, file-backed vector database.
- Retrieve relevant context based on user questions.
- Generate grounded answers using retrieved notes when an LLM is configured.
- Keep the workflow local-first and privacy-aware.
- Stay readable: the entire source fits in three short Python files.

## Architecture

```txt
                          INGEST (offline)
                          --------------

   data/sample_notes/*.md            src/ingest.py                ./chroma_db/
   +-------------------+             +-------------------+         +-----------+
   | local-first-ai.md |  -- load -> | chunk_markdown()  |  --->  | Chroma    |
   | ai-agents.md      |             | embed + upsert    |         | Persistent|
   | personal-knowledge|             +-------------------+         | Client    |
   +-------------------+                                           +-----------+


                          QUERY (every CLI run)
                          ---------------------

   $ python src/query.py "..."        src/query.py                Ollama (optional)
   +-------------------+              +---------------------+     +-------------+
   | user question     |     --->     | embed question      |     | llama3.1    |
   | (CLI argv)        |              | query top-k chunks  |     | /api/       |
   +-------------------+              | build prompt        | --> | generate    |
                                      | call Ollama (opt)   |     +-------------+
                                      | print answer        |
                                      +---------------------+
```

See `docs/architecture.md` for the full walk-through.

## Tech stack

| Layer        | Choice                                           |
|--------------|--------------------------------------------------|
| Language     | Python 3.10+                                     |
| Vector store | [ChromaDB](https://www.trychroma.com/) (embedded)|
| Embeddings   | ChromaDB `DefaultEmbeddingFunction` (ONNX, local)|
| LLM (opt)    | [Ollama](https://ollama.com/) via HTTP API       |
| Config       | `python-dotenv` + `.env`                         |
| Packaging    | `pip` + virtualenv                               |

Two runtime dependencies (`chromadb`, `python-dotenv`). The Ollama call uses
only the Python standard library.

## Features

- **Local-first**: notes and embeddings stay on disk. No cloud APIs are
  required to run the pipeline.
- **Idempotent ingest**: re-running `ingest.py` rebuilds the collection
  from scratch, so the index always reflects the current state of the notes
  directory.
- **Inspectable retrieval**: every query prints the retrieved chunks with
  their source file, chunk index, and cosine distance.
- **Graceful LLM fallback**: if Ollama is unreachable or `LLM_MODEL` is
  empty, the CLI prints retrieved chunks plus an extractive summary. The
  pipeline is useful without an LLM.
- **Composable**: chunking, embedding, retrieval, and generation are
  separate functions, each swappable.

## How to run

### Prerequisites

- Python 3.10 or newer.
- `pip`.
- Optional: [Ollama](https://ollama.com/) for LLM answers.

### Setup

```bash
cd projects/rag-notes
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: edit values if you need to
```

### Build the index

```bash
python src/ingest.py
```

Expected output:

```txt
[ingest] Notes path:   .../data/sample_notes
[ingest] Chroma path:  .../chroma_db
[ingest] Collection:   private_notes
[ingest] Chunk size:   800 (overlap 120)
[ingest] Loaded 3 markdown file(s)
[ingest] Adding N chunk(s) to 'private_notes'
[ingest] Done. Collection size: N
```

### Ask a question

Without an LLM (always works):

```bash
python src/query.py "What are the benefits of local-first AI?"
```

With Ollama:

```bash
# In a separate terminal:
ollama serve
ollama pull llama3.1

# Then run the same query command. The CLI detects Ollama automatically
# when LLM_MODEL is set in .env.
```

See `examples/sample-query.md` for more queries and
`examples/sample-output.md` for realistic transcripts.

## Security and privacy notes

- **No data leaves the machine** unless Ollama is configured. Even then,
  only the prompt (question + retrieved chunks) is sent to the local
  Ollama server.
- **No real notes are shipped.** The `data/sample_notes/` directory
  contains three hand-written synthetic notes. Do not commit real notes
  to this repository.
- **No secrets in the repo.** `.env` is git-ignored. `.env.example`
  contains safe defaults and is the source of truth for configuration.
- **No auth, no encryption.** See `docs/limitations.md` for the honest
  threat-model scope.
- **Chroma DB on disk.** The `./chroma_db` directory contains the vector
  index in plaintext (ChromaDB's native format). Treat it with the same
  care as the source notes.

## Limitations

See `docs/limitations.md` for the full list. Short version:

- Not production-ready. No auth, no encryption at rest, no multi-user.
- No automated evaluation. Manual checks only.
- No reranker, no hybrid search, no metadata filtering.
- Synthetic notes only.
- LLM is optional and best-effort.

## Future improvements

Concrete next steps, in rough order of value:

1. **Metadata filtering** by source file or tag, so queries can be scoped.
2. **Incremental ingest** that detects changed files and updates only those.
3. **Hybrid retrieval** (BM25 + dense) with a small reranker.
4. **Streaming LLM responses** from Ollama.
5. **Automated evaluation harness** with a held-out question set.
6. **Pluggable embeddings** so users can swap in stronger models
   (`bge-large`, `nomic-embed`, etc.).
7. **Optional encryption at rest** for the vector store.
8. **Web UI** that exposes the same pipeline as a local-only chat.

## Project layout

```txt
projects/rag-notes/
├── README.md                    this file
├── docs/
│   ├── architecture.md          end-to-end flow walk-through
│   ├── design-decisions.md      trade-offs and choices
│   ├── evaluation.md            manual evaluation criteria
│   └── limitations.md           honest scope
├── src/
│   ├── config.py                loads .env, exposes constants
│   ├── ingest.py                load, chunk, embed, persist
│   └── query.py                 retrieve, optionally generate, print
├── examples/
│   ├── sample-query.md          example questions
│   └── sample-output.md         realistic transcripts
├── data/
│   └── sample_notes/            synthetic markdown corpus
├── assets/                      reserved for diagrams or screenshots
├── .env.example                 configuration template
├── requirements.txt             two runtime dependencies
└── docker-compose.yml           optional ChromaDB server
```

## License and attribution

This is a personal PoC. No license is granted by default. The synthetic
sample notes were authored specifically for this repository and are not
derived from any real personal knowledge base.

---

**Status: PoC / Experimental.**
Treat outputs as drafts, not as facts. Verify before relying on any
generated answer.