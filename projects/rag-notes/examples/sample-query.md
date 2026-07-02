# Example queries

These are realistic questions you can throw at the PoC after running the
ingest step. They are intentionally tied to the three sample notes shipped in
`data/sample_notes/`.

## 1. Benefits of local-first AI

```bash
python src/query.py "What are the benefits of local-first AI?"
```

Expected to retrieve chunks from `local-first-ai.md`, focusing on the
"Core principles", "Practical benefits", and "When it makes sense" sections.

## 2. Anatomy of an AI agent

```bash
python src/query.py "What are the main parts of an AI agent?"
```

Expected to retrieve chunks from `ai-agents.md`, focusing on
"Anatomy of an agent" and "Common patterns".

## 3. Linking over folders

```bash
python src/query.py "Why is linking notes better than organizing them in folders?"
```

Expected to retrieve chunks from `personal-knowledge.md`, focusing on the
"Linking over folders" and "Retrieval matters more than capture" sections.

## 4. Mixed retrieval (no single home)

```bash
python src/query.py "How can AI agents help with personal knowledge management?"
```

Expected to retrieve chunks from both `ai-agents.md` ("Why they matter for
notes") and `personal-knowledge.md` ("Retrieval matters more than capture").

## Without an LLM

All four queries work even when Ollama is not running. In that case
`query.py` prints the retrieved chunks in full and falls back to an
extractive summary (first line of each chunk). See `sample-output.md` for
realistic output.