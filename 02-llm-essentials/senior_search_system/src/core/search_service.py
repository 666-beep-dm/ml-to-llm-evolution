"""
SearchService — оркестратор: embedder + repository + background indexing.
"""

import asyncio
import logging
from dataclasses import dataclass

import numpy as np

from src.core.embedder import encode_texts
from src.db.base_repository import AbstractVectorRepository, SearchHit
from src.schemas.documents import (
    AddDocumentsRequest, AddDocumentsResponse,
    SearchResult, SearchResponse, DeleteResponse,
)

logger = logging.getLogger(__name__)


@dataclass
class IndexTask:
    doc_id: str
    text: str
    vector: np.ndarray


class SearchService:

    def __init__(self, repository: AbstractVectorRepository) -> None:
        self._repo = repository
        self._task_queue: asyncio.Queue[IndexTask] = asyncio.Queue()
        self._worker: asyncio.Task | None = None

    async def start(self) -> None:
        self._worker = asyncio.create_task(
            self._background_indexer(), name="background-indexer"
        )
        logger.info("Фоновый воркер индексации запущен.")

    async def stop(self) -> None:
        if self._worker:
            self._worker.cancel()
            try:
                await self._worker
            except asyncio.CancelledError:
                pass
        logger.info("Фоновый воркер остановлен.")

    async def _background_indexer(self) -> None:
        while True:
            try:
                task: IndexTask = await self._task_queue.get()
                await asyncio.get_event_loop().run_in_executor(
                    None, self._repo.add, task.doc_id, task.text, task.vector
                )
                self._task_queue.task_done()
                logger.debug("Проиндексирован doc_id='%s'", task.doc_id)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.exception("Ошибка в background indexer: %s", exc)

    async def add_documents(self, request: AddDocumentsRequest) -> AddDocumentsResponse:
        texts = [doc.text for doc in request.documents]
        doc_ids = [doc.doc_id for doc in request.documents]

        # Батч-кодирование всех текстов сразу
        vectors: np.ndarray = await asyncio.get_event_loop().run_in_executor(
            None, encode_texts, texts
        )

        skipped = 0
        added = 0

        # Получаем существующие doc_id через публичный метод, не через приватное поле
        existing_count_before = self._repo.count()

        for doc_id, text, vector in zip(doc_ids, texts, vectors):
            # Добавляем в очередь; репозиторий сам проверит дубли
            await self._task_queue.put(IndexTask(doc_id=doc_id, text=text, vector=vector))

        # Ждём обработки всей очереди
        await self._task_queue.join()

        total = self._repo.count()
        added = total - existing_count_before
        skipped = len(doc_ids) - added

        logger.info(
            "Добавлено: %d, пропущено дублей: %d, всего в индексе: %d",
            added, skipped, total,
        )
        return AddDocumentsResponse(added=added, total_indexed=total, skipped_duplicates=skipped)

    async def search(self, query: str, top_k: int) -> SearchResponse:
        logger.info("Поиск: '%s', top_k=%d", query, top_k)

        query_vectors = await asyncio.get_event_loop().run_in_executor(
            None, encode_texts, [query]
        )
        query_vector = query_vectors[0]

        hits: list[SearchHit] = await asyncio.get_event_loop().run_in_executor(
            None, self._repo.search, query_vector, top_k
        )

        results = [
            SearchResult(doc_id=h.doc_id, text=h.text, score=round(h.score, 6))
            for h in hits
        ]
        return SearchResponse(query=query, results=results, total_indexed=self._repo.count())

    async def delete_all(self) -> DeleteResponse:
        deleted = await asyncio.get_event_loop().run_in_executor(
            None, self._repo.delete_all
        )
        return DeleteResponse(
            deleted=deleted,
            message=f"Удалено {deleted} документов. Индекс очищен."
        )
