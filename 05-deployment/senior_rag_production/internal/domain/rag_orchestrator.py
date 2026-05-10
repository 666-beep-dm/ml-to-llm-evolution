"""
RAG Orchestrator — core domain service.

Pipeline: Cache check -> Vector retrieval -> LLM stream -> Cache write.
No imports from infra or app layers.
"""

import logging
import time
from typing import AsyncGenerator, Protocol, runtime_checkable

from app.schemas.chat import Message
from internal.domain.entities import RAGContext
from internal.domain.exceptions import LLMStreamError, RAGRetrievalError
from app.api.metrics import increment

logger = logging.getLogger(__name__)

_RAG_SYSTEM = """You are a precise AI assistant. Answer the user's question using ONLY the
provided context. Cite sources where relevant.

Context:
{context}
"""

_NO_CONTEXT_SYSTEM = (
    "You are a helpful assistant. No matching documents were found in the "
    "knowledge base. Answer from general knowledge and state this clearly."
)


@runtime_checkable
class CachePort(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl: int) -> None: ...
    async def ping(self) -> str: ...


@runtime_checkable
class VectorStorePort(Protocol):
    async def retrieve(
        self, query: str, collection: str, top_k: int, score_threshold: float
    ) -> RAGContext: ...
    async def ping(self) -> str: ...


@runtime_checkable
class LLMPort(Protocol):
    async def stream(
        self, system: str, messages: list[dict[str, str]]
    ) -> AsyncGenerator[str, None]: ...


class RAGOrchestrator:
    """Stateless domain service — coordinates the full RAG pipeline."""

    def __init__(
        self,
        cache: CachePort,
        vector_store: VectorStorePort,
        llm: LLMPort,
        top_k: int = 4,
        score_threshold: float = 0.35,
        cache_ttl: int = 3600,
    ) -> None:
        self._cache = cache
        self._vector_store = vector_store
        self._llm = llm
        self._top_k = top_k
        self._score_threshold = score_threshold
        self._cache_ttl = cache_ttl

    async def stream_answer(
        self,
        question: str,
        history: list[Message],
        collection: str,
        cache_key: str,
    ) -> AsyncGenerator[str, None]:
        increment("ask_total")

        # ── 1. Cache lookup ──────────────────────────────────────────────
        cached = await self._cache.get(cache_key)
        if cached is not None:
            increment("cache_hits")
            logger.info("cache_hit", extra={"key": cache_key[:12]})
            async for token in _replay(cached):
                yield token
            return

        increment("cache_misses")

        # ── 2. Vector retrieval ──────────────────────────────────────────
        t0 = time.perf_counter()
        try:
            rag_ctx = await self._vector_store.retrieve(
                query=question,
                collection=collection,
                top_k=self._top_k,
                score_threshold=self._score_threshold,
            )
        except Exception as exc:
            raise RAGRetrievalError(f"Retrieval failed: {exc}") from exc

        retrieval_ms = (time.perf_counter() - t0) * 1000
        increment("rag_retrievals")
        logger.info(
            "retrieval_done",
            extra={
                "chunks": len(rag_ctx.chunks),
                "retrieval_ms": round(retrieval_ms, 1),
            },
        )

        # ── 3. Build messages ────────────────────────────────────────────
        system = (
            _RAG_SYSTEM.format(context=rag_ctx.as_context_string())
            if not rag_ctx.is_empty
            else _NO_CONTEXT_SYSTEM
        )
        messages = [
            {"role": m.role, "content": m.content} for m in history
        ] + [{"role": "user", "content": question}]

        # ── 4. Stream LLM ────────────────────────────────────────────────
        t1 = time.perf_counter()
        full_tokens: list[str] = []

        try:
            async for token in self._llm.stream(system, messages):
                full_tokens.append(token)
                yield token
        except Exception as exc:
            increment("stream_errors")
            raise LLMStreamError(f"LLM stream error: {exc}") from exc

        generation_ms = (time.perf_counter() - t1) * 1000
        logger.info(
            "generation_done",
            extra={"generation_ms": round(generation_ms, 1)},
        )

        # ── 5. Async cache write (non-blocking) ──────────────────────────
        if full_tokens:
            try:
                await self._cache.set(
                    cache_key, "".join(full_tokens), ttl=self._cache_ttl
                )
            except Exception as exc:
                logger.warning("cache_write_failed", extra={"error": str(exc)})


async def _replay(text: str) -> AsyncGenerator[str, None]:
    """Re-stream a cached response word-by-word."""
    words = text.split(" ")
    for i, word in enumerate(words):
        yield word if i == len(words) - 1 else word + " "
