"""
Слой получения эмбеддингов.

- Singleton модели через lru_cache (загружается один раз).
- Собственный dict-кэш эмбеддингов: text -> np.ndarray (до 10 000 записей, FIFO-вытеснение).
- Батчевое кодирование: все cache-miss тексты кодируются ОДНИМ вызовом model.encode().
"""

import logging
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
CACHE_MAXSIZE = 10_000

# Простой dict-кэш: text -> np.ndarray float32
# Python 3.7+ гарантирует порядок вставки — FIFO-вытеснение работает через next(iter(...))
_embedding_cache: dict[str, np.ndarray] = {}


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    """Загружает модель один раз и кэширует её на весь жизненный цикл процесса."""
    logger.info("Загрузка модели %s...", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)
    logger.info("Модель загружена. Размерность: %d", EMBEDDING_DIM)
    return model


def encode_texts(texts: list[str]) -> np.ndarray:
    """
    Кодирует список текстов с кэшем и батчингом.

    Алгоритм:
    1. Для каждого текста проверяем dict-кэш — O(1).
    2. Все cache-miss тексты кодируем ОДНИМ батчем (эффективно для CPU/GPU).
    3. Сохраняем результаты в кэш (с FIFO-вытеснением при переполнении).
    4. Возвращаем матрицу [N, EMBEDDING_DIM] в исходном порядке.

    Args:
        texts: Список строк для кодирования.

    Returns:
        np.ndarray shape [len(texts), EMBEDDING_DIM], dtype float32.
    """
    result: list[np.ndarray | None] = [None] * len(texts)
    uncached_indices: list[int] = []
    uncached_texts: list[str] = []

    # Шаг 1: заполняем из кэша
    for i, text in enumerate(texts):
        cached = _embedding_cache.get(text)
        if cached is not None:
            result[i] = cached
        else:
            uncached_indices.append(i)
            uncached_texts.append(text)

    # Шаг 2: батч-кодирование для cache-miss
    if uncached_texts:
        logger.debug("Cache-miss: батч-кодирование %d текстов.", len(uncached_texts))
        model = _load_model()
        batch_vectors: np.ndarray = model.encode(
            uncached_texts,
            batch_size=64,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype(np.float32)

        # Шаг 3: сохраняем в кэш и заполняем результат
        for idx, (orig_i, text) in enumerate(zip(uncached_indices, uncached_texts)):
            vec = batch_vectors[idx]
            result[orig_i] = vec

            # FIFO-вытеснение при переполнении
            if len(_embedding_cache) >= CACHE_MAXSIZE:
                oldest_key = next(iter(_embedding_cache))
                del _embedding_cache[oldest_key]
            _embedding_cache[text] = vec

    return np.vstack(result).astype(np.float32)


def get_embedding_dim() -> int:
    """Возвращает размерность эмбеддингов текущей модели."""
    return EMBEDDING_DIM
