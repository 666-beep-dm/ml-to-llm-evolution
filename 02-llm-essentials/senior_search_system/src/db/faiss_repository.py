"""
FAISS-реализация AbstractVectorRepository (in-memory MVP).

IndexFlatIP = точный поиск по inner product.
Для нормализованных векторов inner product == cosine similarity.
Инкрементальное добавление: faiss.IndexFlatIP.add() без пересборки индекса.
Thread-safety: threading.Lock.
"""

import logging
import threading

import faiss
import numpy as np

from src.db.base_repository import AbstractVectorRepository, SearchHit
from src.core.embedder import get_embedding_dim

logger = logging.getLogger(__name__)


class FAISSRepository(AbstractVectorRepository):

    def __init__(self) -> None:
        dim = get_embedding_dim()
        self._index: faiss.IndexFlatIP = faiss.IndexFlatIP(dim)
        self._metadata: dict[str, tuple[int, str]] = {}   # doc_id -> (faiss_idx, text)
        self._idx_to_doc_id: dict[int, str] = {}
        self._lock = threading.Lock()
        logger.info("FAISSRepository инициализирован. Размерность: %d", dim)

    def add(self, doc_id: str, text: str, vector: np.ndarray) -> bool:
        with self._lock:
            if doc_id in self._metadata:
                return False
            faiss_idx = self._index.ntotal
            self._index.add(vector.reshape(1, -1).astype(np.float32))
            self._metadata[doc_id] = (faiss_idx, text)
            self._idx_to_doc_id[faiss_idx] = doc_id
            return True

    def search(self, query_vector: np.ndarray, top_k: int) -> list[SearchHit]:
        with self._lock:
            if self._index.ntotal == 0:
                return []
            k = min(top_k, self._index.ntotal)
            scores, indices = self._index.search(
                query_vector.reshape(1, -1).astype(np.float32), k
            )
            results = []
            for score, faiss_idx in zip(scores[0], indices[0]):
                if faiss_idx == -1:
                    continue
                doc_id = self._idx_to_doc_id.get(faiss_idx)
                if doc_id is None:
                    continue
                _, text = self._metadata[doc_id]
                results.append(SearchHit(doc_id=doc_id, text=text, score=float(score)))
            return results

    def delete_all(self) -> int:
        with self._lock:
            deleted = self._index.ntotal
            self._index = faiss.IndexFlatIP(self._index.d)
            self._metadata.clear()
            self._idx_to_doc_id.clear()
            logger.info("Индекс очищен. Удалено: %d", deleted)
            return deleted

    def count(self) -> int:
        with self._lock:
            return self._index.ntotal
