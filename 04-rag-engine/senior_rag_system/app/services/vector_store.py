"""
ChromaDB vector store service.
Handles storage and retrieval of document chunks + metadata.
"""

from typing import Any
from uuid import UUID
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.core.logging import logger
from app.models import MetadataFilter, RetrievedChunk


def _get_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _get_collection(client: chromadb.HttpClient) -> chromadb.Collection:
    return client.get_or_create_collection(
        name=settings.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )


def store_chunks(
    document_id: UUID,
    source: str,
    chunks: list[str],
    embeddings: list[list[float]],
    extra_metadata: dict[str, Any],
) -> int:
    """Upsert chunks into ChromaDB. Returns number of chunks stored."""
    from datetime import datetime, timezone

    client = _get_client()
    collection = _get_collection(client)

    ids: list[str] = []
    metadatas: list[dict] = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{document_id}_{i}"
        ids.append(chunk_id)
        metadatas.append(
            {
                "document_id": str(document_id),
                "source": source,
                "chunk_index": i,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                **{k: str(v) for k, v in extra_metadata.items()},
            }
        )

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    logger.info("Stored {} chunks for document_id={}", len(chunks), document_id)
    return len(chunks)


def search(
    query_embedding: list[float],
    top_k: int,
    filters: list[MetadataFilter],
) -> list[RetrievedChunk]:
    """
    Similarity search with optional metadata filtering.

    Returns chunks ordered by cosine similarity (most relevant first).
    """
    client = _get_client()
    collection = _get_collection(client)

    where: dict | None = None
    if filters:
        conditions = [{"$eq": {f.key: f.value}} for f in filters]  # type: ignore[dict-item]
        where = {"$and": conditions} if len(conditions) > 1 else {filters[0].key: filters[0].value}  # type: ignore[assignment]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    chunks: list[RetrievedChunk] = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    for doc, meta, dist, cid in zip(docs, metas, distances, ids):
        chunks.append(
            RetrievedChunk(
                chunk_id=cid,
                content=doc,
                source=meta.get("source", ""),
                document_id=meta.get("document_id", ""),
                score=round(1.0 - dist, 4),  # convert distance → similarity
            )
        )

    return chunks


def health_check() -> bool:
    """Return True if ChromaDB is reachable."""
    try:
        _get_client().heartbeat()
        return True
    except Exception:
        return False
