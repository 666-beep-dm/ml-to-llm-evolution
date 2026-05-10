# Mini-RAG Service

A production-grade **Retrieval-Augmented Generation** microservice built with FastAPI,
ChromaDB, and `sentence-transformers`. Upload documents, then ask questions — the
service retrieves the most relevant context and generates grounded answers via any
OpenAI-compatible LLM (including local Ollama).

---

## Recommended Hardware

| Resource | Recommended |
|----------|-------------|
| RAM      | 16 GB       |
| GPU VRAM | 4 GB        |
| CPU      | 4 cores     |
| Storage  | 10 GB SSD   |
| Python   | 3.10+       |
| Docker   | 24.x+       |

> The default embedding model (`all-MiniLM-L6-v2`) fits comfortably in 4 GB VRAM
> and runs well on CPU-only machines too.

---

## Project Structure

```
middle-rag-service/
├── app/
│   ├── api/
│   │   ├── middleware.py     # Request logging + exception handlers
│   │   ├── routes.py         # POST /upload, POST /ask
│   │   └── schemas.py        # Pydantic v2 schemas
│   ├── core/
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── logging.py        # Structured logging → logs/app.log
│   │   └── prompts.py        # PromptTemplate definitions
│   ├── services/
│   │   ├── document_processor.py  # Text extraction + chunking
│   │   ├── embeddings.py          # Singleton embedding service
│   │   ├── llm_client.py          # Async httpx LLM client
│   │   ├── rag_service.py         # RAG orchestration
│   │   └── vector_store.py        # ChromaDB wrapper
│   └── main.py
├── data/                     # Sample .txt documents
├── vector_db/                # ChromaDB persistence (git-ignored)
├── logs/                     # app.log (git-ignored)
├── tests/
│   └── test_routes.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Quick Start

### Option A — Docker Compose (recommended)

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env: set OPENAI_API_KEY (or configure Ollama endpoint)

# 2. Build and run
docker-compose up --build -d

# 3. Check logs
docker-compose logs -f
```

### Option B — Local development

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # configure your keys
uvicorn app.main:app --reload --port 8000
```

Swagger UI: **http://localhost:8000/docs**

---

## API Reference

### `POST /upload` — Ingest a document

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@./data/sample_rag.txt"
```

```json
{
  "filename": "sample_rag.txt",
  "chunks_stored": 4,
  "total_in_db": 4,
  "message": "Document ingested successfully."
}
```

### `POST /ask` — Query the knowledge base

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG and how does it work?"}'
```

```json
{
  "answer": "RAG (Retrieval-Augmented Generation) combines ...",
  "sources": [
    {"source": "sample_rag.txt", "score": 0.9231}
  ],
  "context_used": true
}
```

### `GET /` — Health check

```bash
curl http://localhost:8000/
```

---

## Using Ollama (local LLM)

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3`
3. In `.env`:

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
MODEL_NAME=llama3
```

4. Restart: `docker-compose up -d`

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Git Bash — Push to GitHub

```bash
# 1. Initialize repository
git init

# 2. Stage all files
git add .

# 3. Commit
git commit -m "feat: middle-level rag service"

# 4. Push to GitHub
git remote add origin https://github.com/<your-username>/middle-rag-service.git
git branch -M main
git push -u origin main

# 5. Build and run
docker-compose up --build -d
```

---

## Architecture

```
Client
  │
  ▼
FastAPI (RequestLoggingMiddleware)
  │
  ├── POST /upload
  │     └── DocumentProcessor (extract → RecursiveCharacterTextSplitter)
  │           └── VectorStore (ChromaDB) ← EmbeddingService (MiniLM-L6-v2)
  │
  └── POST /ask
        ├── VectorStore.query (cosine similarity top-k)
        ├── PromptTemplate.render (context + question)
        └── LLMClient (async httpx → OpenAI / Ollama)
```

---

## License

MIT
