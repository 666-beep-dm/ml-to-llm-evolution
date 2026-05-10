"""Shared pytest fixtures."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.rag_service import RAGService


@pytest.fixture
def mock_rag():
    return MagicMock(spec=RAGService)


@pytest.fixture
def client(mock_rag):
    app.state.rag_service = mock_rag
    app.state.vector_store = AsyncMock(count=AsyncMock(return_value=42), ping=AsyncMock(return_value=True))
    app.state.cache = AsyncMock(ping=AsyncMock(return_value=True))
    return TestClient(app)
