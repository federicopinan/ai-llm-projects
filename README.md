# AI / LLM Projects

A practical portfolio of AI and LLM projects focused on personal knowledge management, local AI infrastructure, retrieval-augmented generation, and automation.

These projects were built to explore how AI systems can become useful operational tools: not just chatbots, but searchable memory layers, local assistants, private LLM environments, and RAG pipelines over personal notes.

## Projects

### 1. AI Second Brain

A personal knowledge system designed to capture, organize, and retrieve information using AI-assisted workflows.

The goal is to turn notes, documents, ideas, and research into a structured second brain that can support learning, decision-making, and long-term knowledge reuse.

**Core ideas:**

- AI-assisted note organization
- Personal knowledge management
- Semantic search over notes
- Research and learning workflows
- Long-term memory for personal projects

**Possible stack:**

- Obsidian
- Local markdown notes
- LLM assistants
- Embedding-based retrieval
- Automation workflows

---

### 2. Context-Aware Personal AI Assistant

A workflow-based AI assistant PoC designed to support daily planning, research summarization, task breakdown, and decision support using reusable prompt templates and structured context.

The goal is to make the prompt layer itself a versionable artifact: workflows are plain markdown files that get rendered with user context into a structured prompt, optionally forwarded to a local LLM. The default mode is prompt-only, no autonomous actions, and every output is meant for human review.

**Core ideas:**

- Reusable markdown prompt workflows
- Context injection via CLI flags
- Local-first, prompt-only by default
- Optional Ollama backend for local LLM execution
- Human-in-the-loop by design

**Stack:**

- Python 3.10+ CLI
- Markdown workflows
- python-dotenv
- requests
- Ollama (optional)

Path: `projects/personal-ai-assistant`

---

### 3. RAG of Personal Notes

A Retrieval-Augmented Generation system built over personal notes and documents.

The project focuses on indexing private knowledge, generating embeddings, storing them in a vector database, and querying them through an LLM-powered interface.

**Core ideas:**

- RAG pipeline
- Document ingestion
- Text chunking
- Embeddings
- Vector search
- LLM-based answers grounded in personal notes

**Possible stack:**

- Python
- ChromaDB
- LlamaIndex or LangChain
- Local markdown files
- Local or API-based LLMs

---

### 4. Local LLM Lab

A local LLM environment for running, testing, and comparing open-source models without depending entirely on cloud APIs.

The project focuses on privacy, local inference, model experimentation, and building a foundation for offline AI workflows.

**Core ideas:**

- Local model execution
- Private AI workflows
- Model comparison
- Prompt testing
- Local inference environment

**Possible stack:**

- Ollama
- Open WebUI
- DeepSeek / Llama / Mistral models
- Docker
- Local GPU or CPU inference
