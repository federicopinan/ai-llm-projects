# Local-First AI

Local-first AI refers to running language models, embeddings, and retrieval
pipelines on the user's own machine instead of relying on remote cloud APIs.
The goal is to keep personal data, prompts, and model outputs under the user's
control.

## Why it matters

Personal notes often contain private context: work projects, health notes,
financial planning, and unfinished ideas. Sending that context to a remote API
introduces privacy, residency, and cost concerns that are easy to forget
during everyday use.

## Core principles

A local-first AI workflow typically follows three principles.

First, **data stays on disk**. Notes, embeddings, and vector indexes live in
files the user owns. Backups are ordinary file copies, not vendor exports.

Second, **inference is local**. A model runs on the user's CPU or GPU, so
prompts never leave the machine. Tools like Ollama and llama.cpp make this
practical on consumer hardware.

Third, **the stack is composable**. Each step — chunking, embedding,
retrieval, generation — can be swapped independently. There is no single
locked-in vendor.

## Practical benefits

- No recurring API costs once the hardware is available.
- Works offline, which is useful on the road or in restricted environments.
- Reproducible behavior: the same model and the same notes always produce the
  same embeddings and answers.
- Easier to audit, since the entire pipeline is open source.

## Honest trade-offs

Local models are usually smaller than the best cloud models, so answer
quality may be lower on hard reasoning tasks. Embedding quality also depends
on the chosen model. Local-first is a privacy and cost win, not a free lunch
on quality.

## When it makes sense

Local-first is a strong default for personal knowledge bases, journaling
assistants, and developer tooling. For high-stakes reasoning or large
context windows, a hybrid approach — local retrieval plus an optional cloud
model — can be a reasonable compromise.