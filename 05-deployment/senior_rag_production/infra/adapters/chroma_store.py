"""ChromaDB vector store adapter with OpenAI embeddings."""

import logging
import time

import chromadb
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from internal.domain.entities import RAGContext, RetrievedChunk
from infra.config import settings as cfg

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    def __init__(
        self,
        client: chromadb.AsyncHttpClient,  # type: ignore[name-defined]
        openai_client: AsyncOpenAI,
    ) -> None:
        self._client = client
        self._openai = openai_client

    @classmethod
    async def create(cls) -> "ChromaVectorStore":
        chroma = await chromadb.AsyncHttpClient(  # type: ignore[attr-defined]
            host=cfg.chroma_host,
            port=cfg.chroma_port,
        )
        openai = AsyncOpenAI(api_key=cfg.openai_api_key)
        return cls(chroma, openai)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=0.5, max=4))
    async def _embed(self, text: str) -> list[float]:
        resp = await self._openai.embeddings.create(
            model=cfg.embedding_model, input=text
        )
        return resp.data[0].embedding

    async def retrieve(
        self,
        query: str,
        collection: str,
        top_k: int = 4,
        score_threshold: float = 0.35,
    ) -> RAGContext:
        t0 = time.perf_counter()
        try:
            col = await self._client.get_or_create_collection(collection)
            embedding = await self._embed(query)
            results = await col.query(
                query_embeddings=[embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.error("chroma_query_failed", extra={"error": str(exc)})
            raise

        retrieval_ms = (time.perf_counter() - t0) * 1000
        docs = results.get("documents", [[]])[0] or []
        metas = results.get("metadatas", [[]])[0] or []
        distances = results.get("distances", [[]])[0] or []

        chunks: list[RetrievedChunk] = []
        for doc, meta, dist in zip(docs, metas, distances):
            score = max(0.0, 1.0 - (dist / 2.0))
            if score >= score_threshold and doc:
                chunks.append(
                    RetrievedChunk(
                        text=doc,
                        source=(meta or {}).get("source", "unknown"),
                        score=score,
                    )
                )

        logger.debug(
            "chroma_results",
            extra={"total": len(docs), "kept": len(chunks),
                   "retrieval_ms": round(retrieval_ms, 1)},
        )
        return RAGContext(chunks=chunks, retrieval_ms=retrieval_ms)

    async def ping(self) -> str:
        try:
            await self._client.heartbeat()
            return "ok"
        except Exception:
            return "unavailable"
