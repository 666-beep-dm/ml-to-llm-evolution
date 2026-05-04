"""
Embedding service — wraps sentence-transformers.
Singleton pattern: model is loaded once on first call.
"""

from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import logger


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    logger.info("Loading embedding model: {}", settings.embedding_model)
    return SentenceTransformer(
        settings.embedding_model,
        cache_folder=settings.hf_home,
    )


def embed(texts: list[str]) -> list[list[float]]:
    """Return L2-normalised embeddings for a list of texts."""
    model = _get_model()
    vectors: np.ndarray = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vectors.tolist()


def embed_one(text: str) -> list[float]:
    return embed([text])[0]
