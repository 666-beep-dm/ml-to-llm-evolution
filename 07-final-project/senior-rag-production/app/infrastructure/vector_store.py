"""
Qdrant-backed vector store with clean port/adapter separation.
"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    SearchRequest, Filter, FieldCondition, MatchValue,
)
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import VectorStoreError
from app.core.logging import get_logger

logger = get_logger("vector_store")
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension


@dataclass
class SearchHit:
    id: str
    text: str
    source: str
    score: float
    metadata: dict


# ── Port ──────────────────────────────────────────────────────────────────────

class VectorStorePort(ABC):
    @abstractmethod
    async def add_chunks(
        self, chunks: list[str], embeddings: list[list[float]],
        source: str, metadata: dict | None = None,
    ) -> int: ...

    @abstractmethod
    async def search(self, embedding: list[float], top_k: int) -> list[SearchHit]: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    @abstractmethod
    async def count(self) -> int: ...


# ── Qdrant adapter ────────────────────────────────────────────────────────────

class QdrantVectorStore(VectorStorePort):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncQdrantClient(
            host=settings.qdrant_host, port=settings.qdrant_port, timeout=30
        )
        self._collection = settings.qdrant_collection

    async def init_collection(self) -> None:
        existing = [c.name for c in (await self._client.get_collections()).collections]
        if self._collection not in existing:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("vector_store.collection_created", name=self._collection)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def add_chunks(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        source: str,
        metadata: dict | None = None,
    ) -> int:
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload={
                    "text": text,
                    "source": source,
                    "chunk_index": i,
                    **(metadata or {}),
                },
            )
            for i, (text, emb) in enumerate(zip(chunks, embeddings))
        ]
        try:
            await self._client.upsert(collection_name=self._collection, points=points)
            logger.info("vector_store.chunks_added", source=source, count=len(points))
            return len(points)
        except Exception as exc:
            raise VectorStoreError(f"Failed to upsert chunks: {exc}") from exc

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def search(self, embedding: list[float], top_k: int) -> list[SearchHit]:
        try:
            results = await self._client.search(
                collection_name=self._collection,
                query_vector=embedding,
                limit=top_k,
                with_payload=True,
            )
            return [
                SearchHit(
                    id=str(r.id),
                    text=r.payload.get("text", ""),
                    source=r.payload.get("source", ""),
                    score=r.score,
                    metadata={k: v for k, v in r.payload.items() if k not in ("text", "source")},
                )
                for r in results
            ]
        except Exception as exc:
            raise VectorStoreError(f"Search failed: {exc}") from exc

    async def ping(self) -> bool:
        try:
            await self._client.get_collections()
            return True
        except Exception:
            return False

    async def count(self) -> int:
        try:
            info = await self._client.get_collection(self._collection)
            return info.points_count or 0
        except Exception:
            return 0
