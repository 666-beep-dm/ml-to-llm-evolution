"""HTTP layer tests."""

import pytest
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


async def _fake_stream(*args, **kwargs):
    for token in ["Hello", " world"]:
        yield token


def _make_mock_container():
    c = MagicMock()
    c.settings.model_name = "gpt-4o-mini"
    # All async methods must be AsyncMock
    c.cache.ping = AsyncMock(return_value="ok")
    c.vector_store.ping = AsyncMock(return_value="ok")
    c.close = AsyncMock(return_value=None)
    c.rate_limiter.limiter = MagicMock()
    c.orchestrator.stream_answer = MagicMock(side_effect=_fake_stream)
    return c


@pytest.fixture()
def client():
    mock_container = _make_mock_container()

    # Flush cached modules so app is freshly imported each fixture
    for key in list(sys.modules.keys()):
        if key.startswith("app") or key.startswith("infra"):
            sys.modules.pop(key, None)

    import app.main as main_module

    async def _fake_create():
        return mock_container

    with patch.object(main_module.Container, "create", side_effect=_fake_create):
        application = main_module.create_app()
        with TestClient(application, raise_server_exceptions=False) as c:
            yield c


def test_health_returns_ok(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["redis"] == "ok"


def test_ask_returns_event_stream(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/ask",
        json={"question": "What is the capital of France?"},
    )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")
    assert "data:" in resp.text


def test_ask_empty_question_rejected(client: TestClient) -> None:
    resp = client.post("/api/v1/ask", json={"question": ""})
    assert resp.status_code == 422


def test_metrics_returns_prometheus_format(client: TestClient) -> None:
    resp = client.get("/metrics/app")
    assert resp.status_code == 200
    assert "rag_ask_total" in resp.text
    assert "rag_cache_hits_total" in resp.text
