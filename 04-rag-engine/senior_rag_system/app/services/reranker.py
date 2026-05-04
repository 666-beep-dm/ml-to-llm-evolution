"""
Cross-encoder reranker — refines the initial top-k retrieval results.
"""

from functools import lru_cache
from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.core.logging import logger


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    logger.info("Loading reranker model: {}", settings.reranker_model)
    return CrossEncoder(settings.reranker_model)


def rerank(query: str, passages: list[str]) -> list[float]:
    """
    Score each (query, passage) pair.

    Returns:
        List of float scores, same order as *passages*.
    """
    reranker = _get_reranker()
    pairs = [(query, p) for p in passages]
    scores: list[float] = reranker.predict(pairs).tolist()
    logger.debug("Reranker scores: {}", scores)
    return scores
