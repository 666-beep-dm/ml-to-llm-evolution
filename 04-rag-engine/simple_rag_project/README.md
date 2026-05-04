# Simple RAG Project

Minimal **Retrieval-Augmented Generation** demo in pure Python.  
No LLM — only semantic search via sentence embeddings + cosine similarity.

---

## Project structure

```
simple_rag_project/
├── main.py               # Core RAG logic
├── requirements.txt      # Pinned Python dependencies
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Convenience wrapper for docker run
├── .dockerignore         # Keeps the build context clean
└── README.md
```

---

## Quickstart — Docker (recommended)

### Option A — docker compose (simplest)

```bash
# 1. Build the image
docker compose build

# 2. Run interactively
docker compose run simple-rag
```

The model is cached in `.hf_cache/` next to the project.  
Subsequent runs skip the download entirely.

---

### Option B — plain docker commands

```bash
# Build
docker build -t simple-rag .

# Run (interactive + model cache volume)
docker run -it \
  -v $(pwd)/.hf_cache:/hf_cache \
  simple-rag
```

---

### Useful Docker commands

```bash
# Rebuild from scratch (no cache)
docker compose build --no-cache

# Run in the background and attach later
docker compose up -d
docker attach simple_rag_project-simple-rag-1

# Remove the container but keep the image
docker compose down

# Remove image too
docker compose down --rmi local

# Check image size
docker images simple-rag
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model name |
| `HF_HOME` | `/hf_cache` | Model cache directory inside the container |

Override in `docker-compose.yml` or via `-e` flag:

```bash
docker run -it -e EMBEDDING_MODEL=all-mpnet-base-v2 simple-rag
```

---

## Example session

```
Loading model: all-MiniLM-L6-v2 ...
Using cache dir: /hf_cache
Knowledge base loaded: 10 entries.

=== Simple RAG Search ===
Type your query (or 'quit' to exit).

Your query: What is FastAPI?

[Best match — similarity: 0.7832]
  → FastAPI is a modern, fast web framework for building APIs with Python.

Your query: quit
Goodbye!
```

---

## Local run (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
