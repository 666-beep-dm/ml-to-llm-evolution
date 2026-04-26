"""
Интеграционные тесты API.
pytest + httpx TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.api.dependencies import get_repository


# Фикстура client — одна на всю сессию тестов
@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


# Очищаем индекс перед каждым тестом
@pytest.fixture(autouse=True)
def clear_index(client):  # client здесь гарантирует что app уже запущен
    get_repository().delete_all()
    yield
    get_repository().delete_all()


# ── /health ───────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "indexed_documents" in r.json()


# ── POST /api/v1/documents ────────────────────────────────────────────────────

def test_add_documents_success(client):
    payload = {"documents": [
        {"doc_id": "1", "text": "Python is a great programming language."},
        {"doc_id": "2", "text": "FastAPI makes building APIs easy."},
        {"doc_id": "3", "text": "Machine learning is transforming industries."},
    ]}
    r = client.post("/api/v1/documents", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["added"] == 3
    assert data["total_indexed"] == 3
    assert data["skipped_duplicates"] == 0


def test_add_documents_skips_duplicates(client):
    payload = {"documents": [{"doc_id": "dup", "text": "Some text."}]}
    client.post("/api/v1/documents", json=payload)
    r = client.post("/api/v1/documents", json=payload)
    assert r.status_code == 201
    assert r.json()["skipped_duplicates"] == 1
    assert r.json()["total_indexed"] == 1


def test_add_empty_text_rejected(client):
    payload = {"documents": [{"doc_id": "x", "text": "   "}]}
    assert client.post("/api/v1/documents", json=payload).status_code == 422


def test_add_empty_list_rejected(client):
    payload = {"documents": []}
    assert client.post("/api/v1/documents", json=payload).status_code == 422


def test_add_empty_doc_id_rejected(client):
    payload = {"documents": [{"doc_id": "", "text": "Some text."}]}
    assert client.post("/api/v1/documents", json=payload).status_code == 422


# ── GET /api/v1/search ────────────────────────────────────────────────────────

def test_search_returns_relevant_results(client):
    client.post("/api/v1/documents", json={"documents": [
        {"doc_id": "p1", "text": "Python programming language"},
        {"doc_id": "p2", "text": "Java is also a programming language"},
        {"doc_id": "p3", "text": "Cooking delicious pasta at home"},
    ]})
    r = client.get("/api/v1/search", params={"query": "programming languages", "top_k": 2})
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) <= 2
    # Кулинарный документ не должен быть первым
    if data["results"]:
        assert data["results"][0]["doc_id"] != "p3"


def test_search_empty_index(client):
    r = client.get("/api/v1/search", params={"query": "anything"})
    assert r.status_code == 200
    assert r.json()["results"] == []


def test_search_scores_between_0_and_1(client):
    client.post("/api/v1/documents", json={"documents": [
        {"doc_id": "s1", "text": "Deep learning neural networks"},
    ]})
    r = client.get("/api/v1/search", params={"query": "machine learning"})
    assert r.status_code == 200
    for result in r.json()["results"]:
        assert 0.0 <= result["score"] <= 1.0


def test_search_respects_top_k(client):
    client.post("/api/v1/documents", json={"documents": [
        {"doc_id": f"d{i}", "text": f"Document number {i} about various topics."}
        for i in range(10)
    ]})
    r = client.get("/api/v1/search", params={"query": "document topic", "top_k": 3})
    assert len(r.json()["results"]) <= 3


# ── DELETE /api/v1/documents ──────────────────────────────────────────────────

def test_delete_clears_index(client):
    client.post("/api/v1/documents", json={"documents": [
        {"doc_id": "del1", "text": "Document to delete."}
    ]})
    r = client.delete("/api/v1/documents")
    assert r.status_code == 200
    assert r.json()["deleted"] == 1
    # Поиск после удаления — пустой результат
    sr = client.get("/api/v1/search", params={"query": "document"})
    assert sr.json()["results"] == []


def test_delete_empty_index(client):
    r = client.delete("/api/v1/documents")
    assert r.status_code == 200
    assert r.json()["deleted"] == 0
