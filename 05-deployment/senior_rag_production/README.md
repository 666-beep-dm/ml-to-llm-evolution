# Senior RAG Production API

A **production-ready, streaming RAG system** built with FastAPI.

## Stack

| Layer | Technology |
|---|---|
| HTTP / Streaming | FastAPI + StreamingResponse (SSE) |
| LLM | OpenAI `gpt-4o-mini` |
| Vector DB | ChromaDB (HTTP mode) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Cache + Rate Limit | Redis + SlowAPI |
| Config | pydantic-settings |
| Logging | python-json-logger (structured JSON) |
| Metrics | Prometheus text format (`/metrics/app`) |
| Containers | Docker multi-stage + docker-compose |

---

## Architecture

```
senior_rag_production/
├── app/                    # Interfaces layer
│   ├── api/router.py       # Thin HTTP controllers, SSE wrapper
│   ├── api/metrics.py      # /metrics/app Prometheus endpoint
│   ├── schemas/chat.py     # Pydantic v2 models
│   └── main.py             # App factory + lifespan DI
├── internal/               # Domain layer (zero I/O dependencies)
│   └── domain/
│       ├── rag_orchestrator.py  # Cache -> Retrieve -> Stream
│       ├── entities.py          # RetrievedChunk, RAGContext
│       └── exceptions.py        # Domain exceptions
├── infra/                  # Infrastructure layer (all I/O)
│   ├── adapters/
│   │   ├── redis_cache.py
│   │   ├── chroma_store.py
│   │   ├── openai_llm.py
│   │   └── rate_limiter.py
│   ├── config.py           # pydantic-settings
│   ├── container.py        # DI wiring
│   └── logging_config.py
├── tests/
├── data/                   # ChromaDB persistence (gitignored)
└── logs/                   # App logs (gitignored)
```

---

## Quick Start (Docker)

```bash
# 1. Configure secrets
cp .env.example .env
# Open .env and set: OPENAI_API_KEY=sk-...

# 2. Build and start all services
docker-compose up --build -d

# 3. Check logs
docker-compose logs -f api

# 4. Stop
docker-compose down
```

**Service URLs:**

| Service    | URL                               |
|------------|-----------------------------------|
| API Docs   | http://localhost:8000/docs        |
| Health     | http://localhost:8000/health      |
| Metrics    | http://localhost:8000/metrics/app |
| ChromaDB   | http://localhost:8001             |

---

## API Usage

### Streaming question (SSE)

```bash
curl -N -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is RAG?",
    "history": [],
    "collection": "knowledge_base"
  }'
```

Response stream:
```
data: RAG
data:  stands
data:  for...
data: [DONE]
```

On error:
```
data: [ERROR] LLM stream timed out after 60s.
```

### With conversation history

```bash
curl -N -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can you elaborate?",
    "history": [
      {"role": "user",      "content": "What is RAG?"},
      {"role": "assistant", "content": "RAG stands for..."}
    ]
  }'
```

---

## Local Development (Git Bash)

```bash
# Virtual environment
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
# source venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start only dependencies
docker-compose up redis vector-db -d

# Run with hot-reload
OPENAI_API_KEY=sk-... uvicorn app.main:app --reload

# Tests
pytest tests/ -v
```

---

## SSH Key Generation (GitHub first-time setup)

```bash
ssh-keygen -t ed25519 -C "your@email.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub | clip   # paste at github.com/settings/ssh/new
```

---

## Git — First Push

```bash
cd senior_rag_production

git init
git add .
git commit -m "feat: senior RAG production API with streaming and Redis"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/senior_rag_production.git
git push -u origin main
```

> Verify `.env` is excluded before pushing:
> ```bash
> git status   # .env must NOT be listed
> ```

---

## Edge Cases Handled

| Scenario | Response |
|---|---|
| ChromaDB unreachable | `RAGRetrievalError` → 503 JSON, stream never starts |
| LLM stream drops mid-stream | `[ERROR]` SSE token sent, error logged |
| Empty retrieval results | Fallback system prompt, answers from general knowledge |
| Redis unavailable | Silent cache miss, request continues normally |
| Rate limit exceeded | 429 JSON via SlowAPI |
| Empty / blank question | 422 Pydantic validation error |
| Cache write failure | Warning logged, response unaffected |
