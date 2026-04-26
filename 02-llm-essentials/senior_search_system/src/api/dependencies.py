"""
DI-контейнер. Единственное место сборки графа зависимостей.
Смена бэкенда — правка только этого файла.
"""

from functools import lru_cache

from src.db.faiss_repository import FAISSRepository
from src.db.base_repository import AbstractVectorRepository
from src.core.search_service import SearchService


@lru_cache(maxsize=1)
def get_repository() -> AbstractVectorRepository:
    return FAISSRepository()


@lru_cache(maxsize=1)
def get_search_service() -> SearchService:
    return SearchService(repository=get_repository())
