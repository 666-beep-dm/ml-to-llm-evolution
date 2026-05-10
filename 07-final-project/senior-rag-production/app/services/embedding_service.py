"""
Embedding service with cache-aside pattern.
Single Responsibility: owns embedding computation and caching logic.
"""
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.logging import get_logger
from app.infrastructure.cache import CachePort

logger = get_logger("embedding")


class EmbeddingService:
    def __init__(self, cache: CachePort) -> None:
        self._cache = cache
        settings = get_settings()
        self._ttl = settings.embedding_cache_ttl
        self._model: SentenceTransformer | None = None

    def load(self) -> None:
        model_name = get_settings().embedding_model
        logger.info("embedding.loading", model=model_name)
        self._model = SentenceTransformer(model_name)
        logger.info("embedding.loaded", model=model_name)

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self.load()
        return self._model  # type: ignore[return-value]

    @staticmethod
    def _cache_key(text: str) -> str:
        digest = hashlib.sha256(text.encode()).hexdigest()
        return f"emb:{digest}"

    async def embed_one(self, text: str) -> list[float]:
        key = self._cache_key(text)
        cached = await self._cache.get(key)
        if cached is not None:
            return cached
        vector = self._get_model().encode(text, convert_to_numpy=True).tolist()
        await self._cache.set(key, vector, ttl=self._ttl)
        return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Check cache for each; batch-encode cache misses
        keys = [self._cache_key(t) for t in texts]
        cached = [await self._cache.get(k) for k in keys]

        miss_indices = [i for i, v in enumerate(cached) if v is None]
        if miss_indices:
            miss_texts = [texts[i] for i in miss_indices]
            vectors = self._get_model().encode(miss_texts, convert_to_numpy=True)
            for idx, vec in zip(miss_indices, vectors):
                v = vec.tolist()
                cached[idx] = v
                await self._cache.set(keys[idx], v, ttl=self._ttl)

        return cached  # type: ignore[return-value]
