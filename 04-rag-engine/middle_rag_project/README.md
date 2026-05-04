# Middle RAG Project

A production-ready **Retrieval-Augmented Generation** pipeline built with:

| Layer | Technology |
|---|---|
| Document loading | Custom loader (`.txt`, `.json`) |
| Chunking | LangChain `RecursiveCharacterTextSplitter` |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector store | FAISS |
| LLM | OpenAI **or** Ollama (switchable via `.env`) |
| Orchestration | LangChain |
| Containerisation | Docker + Docker Compose |

---

## Project structure

```
middle_rag_project/
├── data/                   ← put your .txt / .json documents here
│   ├── fastapi_overview.txt
│   └── tech_notes.json
├── src/
│   ├── __init__.py
│   ├── config.py           ← all settings from .env (pydantic-settings)
│   ├── loader.py           ← .txt and .json document loaders
│   ├── ingest.py           ← chunking + embedding + FAISS index
│   ├── retriever.py        ← top-k similarity search
│   ├── llm.py              ← OpenAI / Ollama abstraction
│   └── app.py              ← interactive Q&A loop (entry point)
├── .env.example            ← copy to .env and fill in your values
├── .dockerignore
├── Dockerfile              ← multi-stage build
├── docker-compose.yml      ← rag + ollama services
├── requirements.txt
└── README.md
```

---

## Quick start

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env — choose LLM_PROVIDER and set keys if using OpenAI
```

### 2. Add your documents

Drop `.txt` or `.json` files into the `data/` folder.
Two sample files are included to test immediately.

### 3a. Run with Ollama (default — no API key needed)

```bash
# Build and start both services
docker compose up -d --build

# Pull the model into Ollama (first time only, ~2 GB)
docker compose exec ollama ollama pull llama3.2

# Attach to the interactive RAG session
docker compose run rag
```

### 3b. Run with OpenAI

Edit `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Remove the `depends_on` block in `docker-compose.yml` (Ollama not needed), then:

```bash
docker compose run rag
```

---

## Useful commands

```bash
# Rebuild image after code changes
docker compose build --no-cache

# Force re-index (delete persisted volume)
docker compose down -v && docker compose run rag

# View logs
docker compose logs -f rag

# Check FAISS index volume
docker volume inspect middle_rag_project_faiss_index
```

---

## Configuration reference

All values in `.env`:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `openai` or `ollama` |
| `OPENAI_API_KEY` | — | Required for OpenAI |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model |
| `DATA_DIR` | `/app/data` | Documents directory |
| `FAISS_INDEX_PATH` | `/app/faiss_index` | Persisted index path |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `TOP_K` | `3` | Retrieved chunks per query |

---

## Example session

```
RAG Assistant — type 'quit' to exit

Your question: What is RAG?

── Retrieved 3 chunk(s) ──
  [1] /app/data/tech_notes.json  →  Retrieval-Augmented Generation (RAG) combines a retrieval step…
  [2] /app/data/fastapi_overview.txt  →  FastAPI is a modern, high-performance web framework…
  [3] /app/data/tech_notes.json  →  FAISS (Facebook AI Similarity Search) is a library…

── Answer ──
RAG (Retrieval-Augmented Generation) combines a retrieval step — finding
relevant documents from a vector store — with a generation step — passing
those documents as context to a large language model to produce a grounded answer.

────────────────────────────────────────────────

Your question: quit
Goodbye!
```
