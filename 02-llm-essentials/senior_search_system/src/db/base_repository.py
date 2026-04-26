"""
Абстрактный репозиторий (Repository Pattern).
Позволяет менять бэкенд хранилища без изменения бизнес-логики.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StoredDocument:
    doc_id: str
    text: str


@dataclass(frozen=True)
class SearchHit:
    doc_id: str
    text: str
    score: float


class AbstractVectorRepository(ABC):

    @abstractmethod
    def add(self, doc_id: str, text: str, vector: np.ndarray) -> bool:
        """True — добавлен, False — дубль пропущен."""

    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int) -> list[SearchHit]:
        """Возвращает top_k ближайших, отсортированных по убыванию score."""

    @abstractmethod
    def delete_all(self) -> int:
        """Очищает индекс; возвращает количество удалённых документов."""

    @abstractmethod
    def count(self) -> int:
        """Текущее количество документов в индексе."""
