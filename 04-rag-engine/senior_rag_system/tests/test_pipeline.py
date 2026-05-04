"""
Basic unit tests for the RAG pipeline.
Run: pytest tests/ -v
"""

from unittest.mock import patch, MagicMock
from app.services import chunker


def test_chunker_splits_text():
    text = ("word " * 200).strip()
    chunks = chunker.split(text)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 600   # chunk_size + small tolerance


def test_chunker_empty_text():
    chunks = chunker.split("   ")
    assert chunks == []


def test_chunker_preserves_content():
    text = "Hello world. " * 50
    chunks = chunker.split(text)
    joined = " ".join(chunks)
    # All words should survive chunking
    assert "Hello" in joined
    assert "world" in joined


@patch("app.services.embedder._get_model")
def test_embedder_returns_list_of_floats(mock_model):
    import numpy as np
    mock_instance = MagicMock()
    mock_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])
    mock_model.return_value = mock_instance

    from app.services.embedder import embed
    result = embed(["test text"])
    assert isinstance(result, list)
    assert isinstance(result[0], list)
    assert isinstance(result[0][0], float)
