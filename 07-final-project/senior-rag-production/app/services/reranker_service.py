"""
Cross-encoder reranker service.
Implements two-stage retrieval: broad top-K from vector DB → precise top-N.
"""
import asyncio
from sentence_transformers import CrossEncoder

from app.core.config import get_settings
from app.core.logging import get_logger
from app.infrastructure.vector_store import SearchHit

logger = get_logger("reranker")


class RerankerService:
    def __init__(self) -> None:
        self._model: CrossEncoder | None = None

    def load(self) -> None:
        model_name = get_settings().reranker_model
        logger.info("reranker.loading", model=model_name)
        self._model = CrossEncoder(model_name, max_length=512)
        logger.info("reranker.loaded")

    def _get_model(self) -> CrossEncoder:
        if self._model is None:
            self.load()
        return self._model  # type: ignore[return-value]

    async def rerank(
        self, query: str, hits: list[SearchHit], top_n: int
    ) -> list[SearchHit]:
        """Rerank hits using cross-encoder scores. Runs in thread pool."""
        if not hits:
            return []

        pairs = [(query, h.text) for h in hits]
        model = self._get_model()

        # Run blocking inference in thread pool to not block event loop
        loop = asyncio.get_event_loop()
        scores = await loop.run_in_executor(None, model.predict, pairs)

        ranked = sorted(
            zip(hits, scores.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )

        reranked = []
        for hit, score in ranked[:top_n]:
            hit.score = float(score)
            reranked.append(hit)

        logger.debug("reranker.done", input=len(hits), output=len(reranked))
        return reranked
