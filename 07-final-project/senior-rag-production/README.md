# Production-Ready RAG Service

A **senior-level**, scalable Retrieval-Augmented Generation microservice built with
Clean Architecture, SOLID principles, full async I/O, and a three-container deployment.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI (api:8000)                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐│
│  │ POST /upload│  │  POST /ask   │  │ GET /health /metrics ││
│  └──────┬──────┘  └──────┬───────┘  └──────────────────────┘│
│         │                │                                    │
│  ┌──────▼──────────────────────────────────────────────────┐ │
│  │               RAGService (orchestrator)                 │ │
│  └──┬──────────────────────────────────────────────────────┘ │
│     │  EmbeddingService   RerankerService   PromptRegistry   │
│     │  (MiniLM-L6-v2)     (ms-marco-L-6-v2)                  │
└─────┼────────────────────────────────────────────────────────┘
      │
   ┌──▼──────────┐    ┌──────────────┐
   │   Qdrant    │    │    Redis     │
   │ (vector_db) │    │   (cache)    │
   └─────────────┘    └──────────────┘
```

**Two-stage retrieval**: Qdrant ANN (top-K=10) → CrossEncoder reranking (top-N=3)

---

## Hardware Requirements

| Resource | Required  | Notes                             |
|----------|-----------|-----------------------------------|
| RAM      | 16 GB     | 8 GB minimum for CPU-only mode    |
| GPU VRAM | 4 GB      | NVIDIA GPU; CPU fallback available|
| CPU      | 4 cores   | 2 cores minimum                   |
| Storage  | 20 GB SSD | For models, Qdrant, Redis volumes |
| Python   | 3.10+     |                                   |
| Docker   | 24.x+     | With Compose v2                   |

---

## Project Structure

```
senior-rag-production/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py     GET / and /health
│   │   │   ├── ingest.py     POST /upload
│   │   │   ├── metrics.py    GET /metrics (Prometheus)
│   │   │   └── query.py      POST /ask (+ streaming)
│   │   ├── deps.py           FastAPI DI container
│   │   ├── middleware.py     Observability + exception handlers
│   │   └── schemas.py        Pydantic v2 contracts
│   ├── core/
│   │   ├── config.py         pydantic-settings, validated
│   │   ├── exceptions.py     Domain exception hierarchy
│   │   ├── logging.py        Structured JSON via structlog
│   │   └── prompts.py        PromptRegistry + strategies
│   ├── infrastructure/
│   │   ├── cache.py          Redis + in-memory fallback
│   │   └── vector_store.py   Qdrant async adapter + port
│   ├── services/
│   │   ├── document_processor.py  Extract + RecursiveCharacterTextSplitter
│   │   ├── embedding_service.py   MiniLM + cache-aside
│   │   ├── llm_client.py          httpx async + streaming
│   │   ├── rag_service.py         Orchestrator
│   │   └── reranker_service.py    CrossEncoder two-stage
│   └── main.py               App factory, lifespan, DI wiring
├── data/                     Sample documents
├── logs/                     app logs (git-ignored)
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile                Multi-stage
├── pyproject.toml
└── README.md
```

---

## Quick Start

### 1. Configure

```bash
cp .env.example .env
# Edit .env — set OPENAI_API_KEY
# For local Ollama: set OPENAI_BASE_URL=http://host.docker.internal:11434/v1
```

### 2. Launch

```bash
docker-compose up --build -d
docker-compose logs -f api
```

- **Swagger UI**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### 3. Ingest a document

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@data/sample_rag.txt"
```

### 4. Ask a question

```bash
# Standard
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is two-stage retrieval?"}'

# Streaming (SSE)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain reranking", "stream": true}'
```

---

## Git Bash — Full Setup Guide

### SSH key generation

```bash
# Generate a new ED25519 key
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519

# Start the SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy your public key (paste into GitHub → Settings → SSH Keys)
cat ~/.ssh/id_ed25519.pub
```

### Initialize and push

```bash
# 1. Initialize git repository
git init

# 2. Stage all project files
git add .

# 3. Initial commit
git commit -m "feat: senior production-ready rag service"

# 4. Add remote (replace <your-username>)
git remote add origin git@github.com:<your-username>/senior-rag-production.git

# 5. Push
git branch -M main
git push -u origin main
```

### Build and run

```bash
# Build images and start all services in detached mode
docker-compose up --build -d

# Tail logs
docker-compose logs -f api

# Stop everything
docker-compose down

# Stop and remove volumes (full reset)
docker-compose down -v
```

### Enable GPU support

Uncomment the `runtime: nvidia` block in `docker-compose.yml`, then:

```bash
docker-compose up --build -d
```

---

## Running Tests

```bash
# Local
pip install -e ".[dev]"
pytest tests/ -v --cov=app --cov-report=term-missing

# Inside Docker
docker-compose exec api pytest tests/ -v
```

---

## Observability

| Endpoint     | Purpose                              |
|-------------|--------------------------------------|
| `/health`   | Service + dependency readiness        |
| `/metrics`  | Prometheus counters and histograms    |
| `logs/`     | Structured JSON logs (structlog)      |

Key metrics exposed:
- `rag_requests_total` — request count by endpoint/status
- `rag_request_latency_seconds` — latency histogram
- `rag_chunks_indexed_total` — documents in vector store
- `rag_tokens_used_total` — estimated LLM token usage

---

## License

MIT
