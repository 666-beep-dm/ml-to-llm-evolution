"""Tests for /ask endpoint."""
import pytest
from unittest.mock import AsyncMock
from app.api.schemas import AskResult, SourceRef


def test_ask_success(client, mock_rag):
    mock_rag.answer = AsyncMock(return_value=AskResult(
        answer="RAG combines retrieval and generation.",
        sources=[SourceRef(source="rag.txt", score=0.92)],
        context_used=True,
        latency_ms=210,
    ))
    resp = client.post("/ask", json={"question": "What is RAG?"})
    assert resp.status_code == 200
    assert "answer" in resp.json()


def test_ask_empty_question(client, mock_rag):
    resp = client.post("/ask", json={"question": ""})
    assert resp.status_code == 422
