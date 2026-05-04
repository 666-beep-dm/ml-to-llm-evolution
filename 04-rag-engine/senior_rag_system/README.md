# Senior RAG System

Production-ready **Retrieval-Augmented Generation** API built with FastAPI.

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Chunking | LangChain `RecursiveCharacterTextSplitter` |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB (HTTP client) |
| Reranker | Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) |
| Semantic cache | Redis + cosine similarity |
| LLM | OpenAI **or** Anthropic (switchable via `.env`) |
| Logging | loguru (stdout + JSON file) |

---

## Project structure

```
senior_rag_system/
├── app/
│   ├── core/
│   │   ├── config.py          ← pydantic-settings
│   │   └── logging.py         ← loguru setup
│   ├── routers/
│   │   ├── ingest.py          ← POST /ingest
│   │   ├── query.py           ← POST /query
│   │   └── health.py          ← GET  /health
│   ├── services/
│   │   ├── rag_pipeline.py    ← orchestrator (Facade)
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── reranker.py
│   │   ├── vector_store.py    ← ChromaDB
│   │   ├── cache.py           ← Redis semantic cache
│   │   └── llm.py             ← OpenAI / Anthropic
│   └── models.py              ← Pydantic schemas
├── tests/
│   └── test_pipeline.py
├── logs/                      ← mounted from host
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .dockerignore
```

---

## Quick start

```bash
# 1. Configure
cp .env.example .env
# Fill in OPENAI_API_KEY or ANTHROPIC_API_KEY

# 2. Start all services
docker compose up -d --build

# 3. Check health
curl http://localhost:8000/health

# 4. Ingest a document
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "FastAPI is a modern Python web framework ...",
    "source": "fastapi_docs",
    "metadata": {"author": "tiangolo"}
  }'

# 5. Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is FastAPI?"}'
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## API reference

### `POST /ingest`
| Field | Type | Description |
|---|---|---|
| `content` | string | Raw document text |
| `source` | string | Document origin (URL, filename…) |
| `metadata` | object | Arbitrary key-value metadata |

### `POST /query`
| Field | Type | Default | Description |
|---|---|---|---|
| `question` | string | — | Natural language question |
| `top_k` | int | settings | Override retrieval count |
| `filters` | list | [] | Metadata filters |
| `use_cache` | bool | true | Allow semantic cache |

### `GET /health`
Returns status of ChromaDB and Redis.

---

## Configuration reference (`.env`)

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openai` | `openai` or `anthropic` |
| `OPENAI_API_KEY` | — | Required for OpenAI |
| `ANTHROPIC_API_KEY` | — | Required for Anthropic |
| `CHROMA_HOST` | `chroma` | ChromaDB service hostname |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `CACHE_SIMILARITY_THRESHOLD` | `0.15` | Max cosine distance for cache hit |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `TOP_K` | `5` | Initial retrieval count |
| `RERANK_TOP_N` | `3` | Chunks passed to LLM after reranking |

---

## Running tests

```bash
pip install pytest
pytest tests/ -v
```
