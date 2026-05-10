"""GET /metrics — Prometheus-compatible metrics endpoint."""
from fastapi import APIRouter, Response
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST,
)

router = APIRouter()

# ── Prometheus metrics ────────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "rag_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "rag_request_latency_seconds", "Request latency",
    ["endpoint"], buckets=[.05, .1, .25, .5, 1, 2.5, 5, 10]
)
CHUNKS_INDEXED = Gauge("rag_chunks_indexed_total", "Total chunks in vector store")
TOKENS_USED = Counter("rag_tokens_used_total", "Estimated tokens sent to LLM")


@router.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
