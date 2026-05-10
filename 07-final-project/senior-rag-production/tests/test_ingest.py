"""Tests for /upload endpoint."""
import pytest
from unittest.mock import AsyncMock
from app.api.schemas import UploadResult


def test_upload_txt(client, mock_rag):
    mock_rag.ingest = AsyncMock(return_value=UploadResult(
        filename="test.txt", chunks_stored=5, total_in_db=5
    ))
    resp = client.post("/upload", files={"file": ("test.txt", b"Some content.", "text/plain")})
    assert resp.status_code == 201
    assert resp.json()["chunks_stored"] == 5


def test_upload_unsupported(client, mock_rag):
    from app.core.exceptions import UnsupportedFileTypeError
    mock_rag.ingest = AsyncMock(side_effect=UnsupportedFileTypeError("bad type"))
    resp = client.post("/upload", files={"file": ("test.csv", b"a,b", "text/csv")})
    assert resp.status_code == 415
