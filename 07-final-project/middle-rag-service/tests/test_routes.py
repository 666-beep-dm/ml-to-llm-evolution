"""
Integration-style tests for the RAG API.
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_empty_question():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422  # Pydantic validation


def test_upload_invalid_extension(tmp_path):
    response = client.post(
        "/upload",
        files={"file": ("test.csv", b"col1,col2", "text/csv")},
    )
    assert response.status_code == 415


@patch("app.api.routes.ingest_document", new_callable=AsyncMock)
def test_upload_txt(mock_ingest):
    mock_ingest.return_value = {
        "filename": "test.txt",
        "chunks_stored": 3,
        "total_in_db": 3,
    }
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"Some test content here.", "text/plain")},
    )
    assert response.status_code == 201
    assert response.json()["chunks_stored"] == 3


@patch("app.api.routes.answer_question", new_callable=AsyncMock)
def test_ask_question(mock_answer):
    mock_answer.return_value = {
        "answer": "Paris is the capital of France.",
        "sources": [{"source": "geo.txt", "score": 0.95}],
        "context_used": True,
    }
    response = client.post("/ask", json={"question": "What is the capital of France?"})
    assert response.status_code == 200
    assert "answer" in response.json()
