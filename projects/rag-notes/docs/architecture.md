# Architecture

This PoC implements a classic Retrieval-Augmented Generation (RAG) pipeline
running entirely on the local machine. The architecture is intentionally
small: every step is a single Python function and the only external service
is an optional local LLM.

## End-to-end flow

```
                            INGEST (offline, run once or whenever notes change)
                            ----------------------------------------------------

   data/sample_notes/*.md       src/ingest.py                chroma_db/
   +-------------------+        +-------------------+        +-------------+
   | local-first-ai.md |  --->  |  load .md files   |        | Persistent  |
   | ai-agents.md      |        |  chunk_markdown() |  --->  | Chroma      |
   | personal-         |        |  embed + upsert   |        | collection  |
   |   knowledge.md    |        +-------------------+        | "private_   |
   +-------------------+                                     |  notes"     |
                                                             +-------------+


                            QUERY (every CLI invocation)
                            ------------------------------

   $ python src/query.py "..."        src/query.py                Ollama (optional)
   +-------------------+              +---------------------+     +-------------+
   | user question     |     --->     |  embed question     |     | llama3.1    |
   | (CLI argv)        |              |  query top-k chunks |     | served via  |
   +-------------------+              |  build prompt       | --> | /api/       |
                                      |  call Ollama (opt)  |     | generate    |
                                      |  print answer       |     +-------------+
                                      +---------------------+
```

## Step-by-step

### 1. Document loading

`src/ingest.py` reads every `*.md` file under `NOTES_PATH` (default
`./data/sample_notes`). Each file is treated as a single note. Filenames are
kept as the `source` metadata field so the retriever can cite them back to
the user.

### 2. Chunking

Notes are split into paragraphs by blank lines and packed greedily into
chunks of roughly `CHUNK_SIZE` characters (default 800) with `CHUNK_OVERLAP`
(default 120) characters of tail carried into the next chunk. The chunker
preserves paragraph boundaries and never splits a paragraph mid-sentence
unless the paragraph is itself larger than `CHUNK_SIZE` (safety net).

This is a deliberately simple chunker. It avoids dependencies on dedicated
splitter libraries and is easy to reason about. See `design-decisions.md`
for the trade-offs.

### 3. Embedding and storage

ChromaDB's `DefaultEmbeddingFunction` is used. It runs locally via ONNX
(`all-MiniLM-L6-v2`, ~384 dimensions, ~80 MB on disk). Embeddings are
generated at ingest time and at query time, transparently, by ChromaDB.

Vectors live in a `PersistentClient` store at `CHROMA_PATH` (default
`./chroma_db`) using cosine distance. The collection is named
`COLLECTION_NAME` (default `private_notes`).

The ingest script deletes and recreates the collection on every run, so
re-ingesting always reflects the current state of `NOTES_PATH`.

### 4. Retrieval

At query time, `src/query.py` embeds the user question with the same
embedding function, asks ChromaDB for the top `TOP_K` (default 4) chunks
by cosine distance, and prints each chunk with its `source`, `chunk_index`,
and distance.

### 5. Grounded answer

If `LLM_MODEL` is set in `.env` and Ollama is reachable at
`OLLAMA_BASE_URL`, the retrieved chunks are concatenated into a prompt with
explicit "use only the context, cite sources" instructions, and sent to
Ollama's `/api/generate` endpoint.

If Ollama is not reachable, or `LLM_MODEL` is empty, the CLI prints the
retrieved chunks in full and falls back to an extractive view (first line
of each chunk). The pipeline is still useful without an LLM.

## Components

| Component              | File                | Responsibility                          |
|------------------------|---------------------|-----------------------------------------|
| Configuration          | `src/config.py`     | Load `.env`, expose typed constants     |
| Ingest pipeline        | `src/ingest.py`     | Load, chunk, embed, persist             |
| Query pipeline         | `src/query.py`      | Retrieve, optionally generate, print    |
| Vector store           | ChromaDB            | Persistent local index                  |
| Embedding model        | `DefaultEmbeddingFn`| Local ONNX, no external API             |
| LLM (optional)         | Ollama              | Local HTTP, `/api/generate`             |

## Data flow guarantees

- Notes are never sent to a remote API during ingest or query.
- Embeddings are computed locally.
- The optional LLM call is the only step that can touch the network, and
  only if the user explicitly sets `LLM_MODEL` and runs Ollama.
- ChromaDB persists to disk; deleting `./chroma_db` removes all vectors.