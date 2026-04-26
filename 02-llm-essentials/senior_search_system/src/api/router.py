"""
API-роуты. Не содержат бизнес-логики — только делегирование SearchService.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import get_search_service
from src.core.search_service import SearchService
from src.schemas.documents import (
    AddDocumentsRequest, AddDocumentsResponse,
    SearchResponse, DeleteResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Search Engine"])


@router.post("/documents", response_model=AddDocumentsResponse, status_code=201)
async def add_documents(
    request: AddDocumentsRequest,
    service: SearchService = Depends(get_search_service),
) -> AddDocumentsResponse:
    try:
        return await service.add_documents(request)
    except Exception as exc:
        logger.exception("Ошибка добавления документов: %s", exc)
        raise HTTPException(500, "Внутренняя ошибка при индексировании.") from exc


@router.get("/search", response_model=SearchResponse)
async def search(
    query: str = Query(..., min_length=1),
    top_k: int = Query(default=5, ge=1, le=100),
    service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    if not query.strip():
        raise HTTPException(422, "Параметр 'query' не может быть пустым.")
    try:
        return await service.search(query=query.strip(), top_k=top_k)
    except Exception as exc:
        logger.exception("Ошибка поиска: %s", exc)
        raise HTTPException(500, "Внутренняя ошибка при поиске.") from exc


@router.delete("/documents", response_model=DeleteResponse)
async def delete_all(
    service: SearchService = Depends(get_search_service),
) -> DeleteResponse:
    try:
        return await service.delete_all()
    except Exception as exc:
        logger.exception("Ошибка очистки: %s", exc)
        raise HTTPException(500, "Внутренняя ошибка при очистке индекса.") from exc
