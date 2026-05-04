"""
/health router — liveness and dependency checks.
"""

from fastapi import APIRouter
from app.models import HealthResponse, ComponentStatus
from app.services import vector_store, cache

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    chroma_ok = vector_store.health_check()
    redis_ok = cache.health_check()

    components = {
        "chroma": ComponentStatus(
            status="ok" if chroma_ok else "down",
            detail="" if chroma_ok else "ChromaDB unreachable",
        ),
        "redis": ComponentStatus(
            status="ok" if redis_ok else "down",
            detail="" if redis_ok else "Redis unreachable",
        ),
    }

    overall = "ok" if all(c.status == "ok" for c in components.values()) else "degraded"
    return HealthResponse(status=overall, components=components)
