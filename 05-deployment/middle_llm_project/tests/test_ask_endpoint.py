"""
Minimal unit tests for the /ask endpoint.

Run with:  pytest -v
"""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.schemas.chat import AskResponse


def _make_mock_service() -> AsyncMock:
    """Return a pre-configured mock LLMService."""
    mock = AsyncMock()
    mock.ask.return_value = AskResponse(
        answer="Paris",
        model="gpt-4o-mini",
        prompt_tokens=10,
        completion_tokens=3,
    )
    return mock


@pytest.fixture()
def client():
    """Provide a test client with LLMService patched at construction time."""
    mock_service = _make_mock_service()

    with patch("app.services.llm_service.LLMService", return_value=mock_service):
        from app.main import create_app  # import after patch is active
        application = create_app()
        with TestClient(application) as c:
            yield c


def test_ask_returns_answer(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ask",
        json={"question": "What is the capital of France?", "history": []},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Paris"
    assert data["model"] == "gpt-4o-mini"


def test_ask_with_history(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ask",
        json={
            "question": "And Germany?",
            "history": [
                {"role": "user", "content": "What is the capital of France?"},
                {"role": "assistant", "content": "Paris"},
            ],
        },
    )
    assert response.status_code == 200


def test_ask_empty_question_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/ask", json={"question": "", "history": []})
    assert response.status_code == 422


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
