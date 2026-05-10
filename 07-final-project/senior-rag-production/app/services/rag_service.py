"""
RAG orchestration service.
Coordinates: embed → retrieve → rerank → prompt → generate.
"""
from __future__ import annotations
import time
from typing import AsyncIterator

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.prompts import PromptRegistry
from app.infrastructure.cache import CachePort
from app.infrastructure.vector_store import VectorStorePort
from app.services.document_processor import process_document
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services import llm_client
from app.api.schemas import UploadResult, AskResult, SourceRef

logger = get_logger("rag")


class RAGService:
    def __init__(
        self,
        vector_store: VectorStorePort,
        embedder: EmbeddingService,
        reranker: RerankerService,
        cache: CachePort,
    ) -> None:
        self._vs = vector_store
        self._embedder = embedder
        self._reranker = reranker
        self._cache = cache

    # ── Ingestion ─────────────────────────────────────────────────────────────

    async def ingest(self, filename: str, data: bytes, metadata: dict | None = None) -> UploadResult:
        t0 = time.perf_counter()
        chunks = process_document(filename, data)
        embeddings = await self._embedder.embed_batch(chunks)
        count = await self._vs.add_chunks(chunks, embeddings, source=filename, metadata=metadata)
        total = await self._vs.count()
        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info("rag.ingested", file=filename, chunks=count, elapsed_ms=elapsed)
        return UploadResult(filename=filename, chunks_stored=count, total_in_db=total)

    # ── Non-streaming answer ──────────────────────────────────────────────────

    async def answer(
        self, question: str, prompt_name: str = "rag_default"
    ) -> AskResult:
        cache_key = self._cache.make_key("ask", question, prompt_name)
        cached = await self._cache.get(cache_key)
        if cached:
            logger.debug("rag.cache_hit", question=question[:60])
            return AskResult(**cached)

        t0 = time.perf_counter()
        hits = await self._retrieve_and_rerank(question)
        prompt = PromptRegistry.get(prompt_name if hits else "rag_no_context")
        system, user = prompt.render(question, [h.__dict__ for h in hits])
        answer_text = await llm_client.chat(system, user)
        elapsed = round((time.perf_counter() - t0) * 1000)

        result = AskResult(
            answer=answer_text,
            sources=[SourceRef(source=h.source, score=round(h.score, 4)) for h in hits],
            context_used=bool(hits),
            latency_ms=elapsed,
        )
        await self._cache.set(cache_key, result.model_dump())
        logger.info("rag.answered", elapsed_ms=elapsed, sources=len(hits))
        return result

    # ── Streaming answer ──────────────────────────────────────────────────────

    async def answer_stream(
        self, question: str, prompt_name: str = "rag_default"
    ) -> AsyncIterator[str]:
        hits = await self._retrieve_and_rerank(question)
        prompt = PromptRegistry.get(prompt_name if hits else "rag_no_context")
        system, user = prompt.render(question, [h.__dict__ for h in hits])
        async for delta in llm_client.chat_stream(system, user):
            yield delta

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _retrieve_and_rerank(self, question: str):
        s = get_settings()
        q_emb = await self._embedder.embed_one(question)
        hits = await self._vs.search(q_emb, top_k=s.top_k)
        if hits:
            hits = await self._reranker.rerank(question, hits, top_n=s.rerank_top_n)
        return hits
