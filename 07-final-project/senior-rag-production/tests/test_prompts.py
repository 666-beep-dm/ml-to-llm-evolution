"""Tests for PromptRegistry and PromptTemplate."""
import pytest
from app.core.prompts import PromptRegistry


def test_registry_default():
    prompt = PromptRegistry.get("rag_default")
    hits = [{"text": "Paris is the capital.", "source": "geo.txt", "score": 0.9}]
    system, user = prompt.render("What is the capital?", hits)
    assert "Paris" in user
    assert "capital" in user


def test_registry_missing():
    with pytest.raises(KeyError):
        PromptRegistry.get("nonexistent_prompt")


def test_list_names():
    names = PromptRegistry.list_names()
    assert "rag_default" in names
    assert "rag_concise" in names
