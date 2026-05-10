"""Custom /metrics/app endpoint — Prometheus text format."""

import time
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

metrics_router = APIRouter()

_counters: dict[str, float] = {
    "ask_total": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "rag_retrievals": 0,
    "stream_errors": 0,
    "start_time": time.time(),
}


def increment(key: str, value: float = 1.0) -> None:
    _counters[key] = _counters.get(key, 0) + value


@metrics_router.get(
    "/metrics/app",
    response_class=PlainTextResponse,
    summary="Application counters (Prometheus text format)",
)
async def app_metrics() -> PlainTextResponse:
    uptime = time.time() - _counters["start_time"]
    lines = [
        "# HELP rag_ask_total Total POST /ask requests",
        "# TYPE rag_ask_total counter",
        f"rag_ask_total {int(_counters['ask_total'])}",
        "# HELP rag_cache_hits_total Cache hit count",
        "# TYPE rag_cache_hits_total counter",
        f"rag_cache_hits_total {int(_counters['cache_hits'])}",
        "# HELP rag_cache_misses_total Cache miss count",
        "# TYPE rag_cache_misses_total counter",
        f"rag_cache_misses_total {int(_counters['cache_misses'])}",
        "# HELP rag_retrievals_total Vector DB retrieval count",
        "# TYPE rag_retrievals_total counter",
        f"rag_retrievals_total {int(_counters['rag_retrievals'])}",
        "# HELP rag_stream_errors_total Stream error count",
        "# TYPE rag_stream_errors_total counter",
        f"rag_stream_errors_total {int(_counters['stream_errors'])}",
        "# HELP rag_uptime_seconds Process uptime in seconds",
        "# TYPE rag_uptime_seconds gauge",
        f"rag_uptime_seconds {uptime:.2f}",
    ]
    return PlainTextResponse("\n".join(lines) + "\n")
