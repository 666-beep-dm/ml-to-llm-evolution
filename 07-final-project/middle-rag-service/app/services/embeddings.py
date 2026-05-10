"""
Singleton embedding service using sentence-transformers.
Loaded once at startup; thread-safe for concurrent encode() calls.
"""

from sentence_transformers import SentenceTransformer
from app.core.config import get_settings
from app.core.logging import logger
import numpy as np


class EmbeddingService:
    _instance: "EmbeddingService | None" = None

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self) -> None:
        if self._loaded:
            return
        model_name = get_settings().embedding_model
        logger.info(f"Loading embedding model: {model_name}")
        self._model = SentenceTransformer(model_name)
        self._loaded = True
        logger.info("Embedding model loaded successfully.")

    def encode(self, texts: list[str]) -> list[list[float]]:
        if not self._loaded:
            self.load()
        vectors: np.ndarray = self._model.encode(texts, convert_to_numpy=True)
        return vectors.tolist()

    def encode_one(self, text: str) -> list[float]:
        return self.encode([text])[0]


embedding_service = EmbeddingService()
