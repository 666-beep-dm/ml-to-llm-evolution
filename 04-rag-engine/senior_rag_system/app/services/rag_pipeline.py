"""
RAG pipeline orchestrator — the single entry point for business logic.
Follows the Facade pattern: routers talk only to this module.
"""

import time
from datetime import datetime, timezone
from uuid import uuid4, UUID

from app.core.config import settings
from app.core.logging import logger
from app.models import (
    IngestRequest, IngestResponse,
    QueryRequest, QueryResponse, RetrievedChunk,
)
from app.services import chunker, embedder, vector_store, cache, reranker, llm


def ingest(request: IngestRequest) -> IngestResponse:
    """Full ingestion pipeline: chunk → embed → store."""
    document_id: UUID = uuid4()
    ingested_at = datetime.now(timezone.utc)

    logger.info("Ingesting document source='{}' id={}", request.source, document_id)

    # 1. Chunk
    chunks = chunker.split(request.content)
    logger.debug("{} chunks created", len(chunks))

    # 2. Embed
    embeddings = embedder.embed(chunks)

    # 3. Store
    stored = vector_store.store_chunks(
        document_id=document_id,
        source=request.source,
        chunks=chunks,
        embeddings=embeddings,
        extra_metadata=request.metadata,
    )

    return IngestResponse(
        document_id=document_id,
        chunks_stored=stored,
        source=request.source,
        ingested_at=ingested_at,
    )


def query(request: QueryRequest) -> QueryResponse:
    """Full RAG query pipeline: cache → retrieve → rerank → generate."""
    t0 = time.perf_counter()
    top_k = request.top_k or settings.top_k

    logger.info("Query received: '{}'", request.question[:120])

    # 1. Embed the question
    q_embedding = embedder.embed_one(request.question)

    # 2. Semantic cache lookup
    if request.use_cache:
        hit = cache.get_cached(q_embedding)
        if hit:
            latency_ms = (time.perf_counter() - t0) * 1000
            return QueryResponse(
                answer=hit["answer"],
                chunks_used=[RetrievedChunk(**c) for c in hit["chunks"]],
                cached=True,
                latency_ms=round(latency_ms, 2),
            )

    # 3. Vector search
    retrieved = vector_store.search(
        query_embedding=q_embedding,
        top_k=top_k,
        filters=request.filters,
    )
    logger.info("Retrieved {} chunks from vector store", len(retrieved))

    # 4. Rerank
    if retrieved:
        passages = [c.content for c in retrieved]
        scores = reranker.rerank(request.question, passages)
        for chunk, score in zip(retrieved, scores):
            chunk.rerank_score = round(score, 4)
        # Sort by rerank score descending, keep top rerank_top_n
        retrieved.sort(key=lambda c: c.rerank_score or 0.0, reverse=True)
        retrieved = retrieved[: settings.rerank_top_n]
        logger.info("Reranked to {} chunks", len(retrieved))

    # 5. Generate
    context = [{"content": c.content, "source": c.source} for c in retrieved]
    answer = llm.generate(request.question, context)
    logger.info("Answer generated ({} chars)", len(answer))

    # 6. Store in cache
    payload = {
        "answer": answer,
        "chunks": [c.model_dump() for c in retrieved],
    }
    cache.set_cached(q_embedding, payload)

    latency_ms = (time.perf_counter() - t0) * 1000
    return QueryResponse(
        answer=answer,
        chunks_used=retrieved,
        cached=False,
        latency_ms=round(latency_ms, 2),
    )
