"""Ingest markdown notes into a local ChromaDB collection.

Run:
    python src/ingest.py

The script is idempotent: it deletes the previous collection and rebuilds it
from scratch, so re-running always reflects the current state of the notes
directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as `python src/ingest.py` from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import chromadb
from chromadb.utils import embedding_functions

from config import (
    CHROMA_PATH,
    CHROMA_URL,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    NOTES_PATH,
)


def make_chroma_client() -> chromadb.api.ClientAPI:
    """Return a Chroma client in either embedded or server mode."""
    if CHROMA_URL:
        print(f"[ingest] Using ChromaDB server at {CHROMA_URL}")
        return chromadb.HttpClient(host=CHROMA_URL)
    print(f"[ingest] Using embedded ChromaDB at {CHROMA_PATH}")
    return chromadb.PersistentClient(path=CHROMA_PATH)


def split_markdown_paragraphs(text: str) -> list[str]:
    """Return non-empty paragraphs, splitting on blank lines."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def chunk_markdown(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Group markdown paragraphs into chunks of roughly `chunk_size` characters.

    Strategy:
      1. Split the note into paragraphs.
      2. Greedily pack paragraphs into a buffer while staying under chunk_size.
      3. When the next paragraph would overflow, flush the buffer and start a
         new one, carrying a tail of `overlap` chars to preserve context.
      4. As a safety net, hard-split any remaining oversized chunk.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be in [0, chunk_size)")

    paragraphs = split_markdown_paragraphs(text)
    if not paragraphs:
        return []

    chunks: list[str] = []
    buffer = ""

    for paragraph in paragraphs:
        if not buffer:
            buffer = paragraph
            continue

        if len(buffer) + 2 + len(paragraph) <= chunk_size:
            buffer = f"{buffer}\n\n{paragraph}"
            continue

        chunks.append(buffer)
        tail = buffer[-overlap:] if overlap > 0 else ""
        buffer = f"{tail}\n\n{paragraph}".strip() if tail else paragraph

    if buffer:
        chunks.append(buffer)

    # Safety net for pathological single-paragraph notes.
    final: list[str] = []
    for chunk in chunks:
        if len(chunk) <= chunk_size:
            final.append(chunk)
            continue
        start = 0
        while start < len(chunk):
            end = min(start + chunk_size, len(chunk))
            piece = chunk[start:end].strip()
            if piece:
                final.append(piece)
            if end == len(chunk):
                break
            start = max(end - overlap, start + 1)
    return final


def load_notes(notes_path: Path) -> list[tuple[str, str]]:
    """Read every `*.md` file under `notes_path`, sorted by filename."""
    if not notes_path.exists():
        raise FileNotFoundError(f"Notes directory not found: {notes_path}")
    files = sorted(notes_path.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"No markdown files in {notes_path}")
    return [(f.name, f.read_text(encoding="utf-8")) for f in files]


def reset_collection(client: chromadb.PersistentClient, name: str) -> None:
    """Delete and recreate the collection for an idempotent ingest."""
    try:
        client.delete_collection(name)
    except Exception:
        # Collection does not exist yet — nothing to clean up.
        pass


def main() -> int:
    print(f"[ingest] Notes path:   {NOTES_PATH}")
    print(f"[ingest] Chroma path:  {CHROMA_PATH}")
    print(f"[ingest] Collection:   {COLLECTION_NAME}")
    print(f"[ingest] Chunk size:   {CHUNK_SIZE} (overlap {CHUNK_OVERLAP})")

    notes = load_notes(NOTES_PATH)
    print(f"[ingest] Loaded {len(notes)} markdown file(s)")

    client = make_chroma_client()
    reset_collection(client, COLLECTION_NAME)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_functions.DefaultEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )

    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    for filename, text in notes:
        chunks = chunk_markdown(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for index, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk_index": index})
            ids.append(f"{filename}::{index}")

    if not documents:
        print("[ingest] No chunks produced. Are the markdown files empty?")
        return 1

    print(f"[ingest] Adding {len(documents)} chunk(s) to '{COLLECTION_NAME}'")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"[ingest] Done. Collection size: {collection.count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())