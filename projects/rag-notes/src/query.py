"""Query the local ChromaDB index and answer a question from the CLI.

Run:
    python src/query.py "your question here"

Behavior:
  - Always retrieves the top-k most relevant chunks and prints them with their
    source file, chunk index, and cosine distance.
  - If `LLM_MODEL` is set AND a local Ollama server is reachable, it asks
    Ollama to generate a grounded answer using the retrieved context.
  - Otherwise it prints a grounded "extract" view (first lines of each chunk)
    so the CLI still produces a useful, inspectable result without an LLM.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Allow running as `python src/query.py` from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import chromadb
from chromadb.utils import embedding_functions

from config import (
    CHROMA_PATH,
    CHROMA_URL,
    COLLECTION_NAME,
    LLM_MODEL,
    OLLAMA_BASE_URL,
    TOP_K,
)


def make_chroma_client() -> chromadb.api.ClientAPI:
    """Return a Chroma client in either embedded or server mode."""
    if CHROMA_URL:
        return chromadb.HttpClient(host=CHROMA_URL)
    return chromadb.PersistentClient(path=CHROMA_PATH)


GROUNDED_PROMPT_TEMPLATE = """You are a helpful assistant answering questions about a personal notes collection.
Use ONLY the context provided below. If the context does not contain the answer, say so explicitly.
Cite the source filename in brackets after each claim, like [local-first-ai.md].
Be concise. Do not invent information that is not present in the context.

Context:
{context}

Question: {question}

Answer:"""


def retrieve(collection, question: str, top_k: int) -> dict:
    return collection.query(query_texts=[question], n_results=top_k)


def format_distance(distance) -> str:
    if distance is None:
        return ""
    try:
        return f" | distance: {float(distance):.4f}"
    except (TypeError, ValueError):
        return f" | distance: {distance}"


def print_retrieved_chunks(results: dict) -> None:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if results.get("distances") else []

    if not documents:
        print("[query] No chunks returned by the retriever.")
        return

    print("=" * 72)
    print(f"RETRIEVED CONTEXT (top {len(documents)})")
    print("=" * 72)
    for i, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        distance_str = format_distance(distances[i - 1] if i - 1 < len(distances) else None)
        source = meta.get("source", "unknown")
        idx = meta.get("chunk_index", "?")
        print(f"\n--- Chunk {i} | source: {source} | index: {idx}{distance_str} ---")
        print(doc.strip())


def call_ollama(prompt: str, base_url: str, model: str, timeout: float = 60.0) -> str | None:
    """Call Ollama /api/generate. Returns the generated text or None on failure.

    Returns None on connection error, HTTP error, bad JSON, empty response,
    or any other transport problem — never raises.
    """
    url = f"{base_url.rstrip('/')}/api/generate"
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    text = data.get("response", "").strip()
    return text or None


HEADING_RE = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)


def first_meaningful_line(text: str) -> str:
    """Pick a clean, human-readable first line from a chunk.

    Chunks may begin with overlap tails (mid-word fragments). Prefer the
    first markdown heading in the chunk; otherwise the first sentence-like
    line; otherwise the longest non-empty line.
    """
    match = HEADING_RE.search(text)
    if match:
        return match.group(1).strip()

    for line in text.splitlines():
        stripped = line.strip()
        if len(stripped) > 40 and stripped.endswith((".", ":", "?")):
            return stripped

    candidates = [line.strip() for line in text.splitlines() if line.strip()]
    if not candidates:
        return "(empty chunk)"
    return max(candidates, key=len)


def print_extract_fallback(results: dict) -> None:
    """No-LLM fallback: print a clean, heading-based extract of each chunk."""
    documents = results.get("documents", [[]])[0]
    print("\n(No LLM configured or Ollama is unreachable.)")
    print("Showing a grounded extract (first heading or sentence per chunk):\n")
    for i, doc in enumerate(documents, start=1):
        first_line = first_meaningful_line(doc)
        if len(first_line) > 200:
            first_line = first_line[:197] + "..."
        print(f"  {i}. {first_line}")
    print(
        "\nTo enable LLM answers: install Ollama (https://ollama.com), run it "
        "locally, and ensure LLM_MODEL is set in .env."
    )


def build_context_block(results: dict) -> str:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    blocks = []
    for doc, meta in zip(documents, metadatas):
        source = meta.get("source", "unknown")
        idx = meta.get("chunk_index", "?")
        blocks.append(f"[source: {source} | chunk: {idx}]\n{doc}")
    return "\n\n---\n\n".join(blocks)


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python src/query.py "your question here"')
        return 1

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Empty question.")
        return 1

    chroma_dir = Path(CHROMA_PATH)
    if not CHROMA_URL and not chroma_dir.exists():
        print(f"[query] Chroma DB not found at {chroma_dir}")
        print("[query] Run `python src/ingest.py` first to build the index.")
        return 1

    client = make_chroma_client()
    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_functions.DefaultEmbeddingFunction(),
    )

    print(f"[query] Question: {question}")
    print(f"[query] top_k={TOP_K} | collection='{COLLECTION_NAME}'\n")

    results = retrieve(collection, question, TOP_K)
    print_retrieved_chunks(results)

    if not results.get("documents", [[]])[0]:
        return 0

    print("\n" + "=" * 72)
    print("ANSWER")
    print("=" * 72)

    if LLM_MODEL:
        context = build_context_block(results)
        prompt = GROUNDED_PROMPT_TEMPLATE.format(context=context, question=question)
        answer = call_ollama(prompt, OLLAMA_BASE_URL, LLM_MODEL)
        if answer:
            print(answer)
            print(f"\n[generated by Ollama model: {LLM_MODEL}]")
            return 0
        print(f"(Ollama call failed for model '{LLM_MODEL}' at {OLLAMA_BASE_URL}.)")

    print_extract_fallback(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())