"""
Basic tests for the Mini-RAG API.
Run with: pytest tests/
"""

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_empty_question():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 400


def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200
