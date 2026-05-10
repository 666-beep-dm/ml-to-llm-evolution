"""GET / and GET /health — service health + readiness."""
from fastapi import APIRouter, Request
from app.api.schemas import HealthResult

router = APIRouter()


@router.get("/", response_model=HealthResult, tags=["Health"])
@router.get("/health", response_model=HealthResult, tags=["Health"])
async def health(request: Request) -> HealthResult:
    state = request.app.state
    vs_ok = await state.vector_store.ping()
    cache_ok = await state.cache.ping()
    return HealthResult(
        status="ok" if vs_ok and cache_ok else "degraded",
        vector_store="ok" if vs_ok else "unavailable",
        cache="ok" if cache_ok else "fallback",
        chunks_indexed=await state.vector_store.count(),
    )
