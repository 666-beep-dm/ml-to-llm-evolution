"""
ML-логика: загрузка модели, получение эмбеддингов,
расчёт матрицы косинусного сходства, поиск топ-N пар.
"""

import logging
from itertools import combinations
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util

from app.schemas import SimilarPair

logger = logging.getLogger(__name__)
MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """
    Загружает модель один раз при первом обращении и кэширует её.
    lru_cache гарантирует, что модель не будет перезагружаться на каждый запрос.
    """
    logger.info("Загрузка модели %s...", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)
    logger.info("Модель загружена.")
    return model


def compute_top_pairs(texts: list[str], top_n: int = 3) -> list[SimilarPair]:
    """
    Основная ML-функция сервиса.

    1. Кодирует тексты в эмбеддинги.
    2. Строит полную матрицу косинусного сходства.
    3. Извлекает top_n пар с наивысшим сходством (без диагонали и дублей).

    Args:
        texts:  Список входных текстов (уже провалидированных).
        top_n:  Количество возвращаемых пар.

    Returns:
        Список объектов SimilarPair, отсортированных по убыванию score.
    """
    model = get_model()

    # Получаем эмбеддинги батчем
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

    # Полная матрица сходства N x N
    similarity_matrix = util.cos_sim(embeddings, embeddings).cpu().numpy()

    # Уникальные пары (i < j — без диагонали и дублей)
    pairs: list[tuple[float, int, int]] = []
    for i, j in combinations(range(len(texts)), 2):
        score = float(similarity_matrix[i][j])
        pairs.append((score, i, j))

    # Сортируем по убыванию сходства
    pairs.sort(key=lambda x: x[0], reverse=True)

    result = []
    for score, i, j in pairs[:top_n]:
        result.append(
            SimilarPair(
                index_a=i,
                index_b=j,
                text_a=texts[i],
                text_b=texts[j],
                score=round(score, 6),
            )
        )

    return result
