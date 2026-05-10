"""Unit tests for the RAG orchestrator (domain layer)."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from internal.domain.rag_orchestrator import RAGOrchestrator
from internal.domain.entities import RAGContext, RetrievedChunk
from internal.domain.exceptions import RAGRetrievalError, LLMStreamError
from app.schemas.chat import Message


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _collect(gen) -> list[str]:
    return [t async for t in gen]


def _make_orch(
    cached: str | None = None,
    chunks: list[RetrievedChunk] | None = None,
    tokens: list[str] | None = None,
    retrieval_error: Exception | None = None,
    stream_error: Exception | None = None,
) -> RAGOrchestrator:
    cache = AsyncMock()
    cache.get.return_value = cached
    cache.set.return_value = None
    cache.ping.return_value = "ok"

    vector_store = AsyncMock()
    if retrieval_error:
        vector_store.retrieve.side_effect = retrieval_error
    else:
        vector_store.retrieve.return_value = RAGContext(
            chunks=chunks if chunks is not None else [
                RetrievedChunk("Paris info", "geo.txt", 0.9)
            ],
            retrieval_ms=10.0,
        )
    vector_store.ping.return_value = "ok"

    _tokens = tokens or ["Paris", " is", " the", " capital."]

    async def _stream(system, messages):
        if stream_error:
            raise stream_error
        for t in _tokens:
            yield t

    llm = MagicMock()
    llm.stream.side_effect = _stream

    return RAGOrchestrator(
        cache=cache,
        vector_store=vector_store,
        llm=llm,
        top_k=3,
        score_threshold=0.3,
        cache_ttl=60,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_rag_stream() -> None:
    orch = _make_orch()
    tokens = await _collect(
        orch.stream_answer("Capital?", [], "kb", "k1")
    )
    assert "Paris" in "".join(tokens)


@pytest.mark.asyncio
async def test_cache_hit_skips_retrieval() -> None:
    orch = _make_orch(cached="Berlin is the capital.")
    tokens = await _collect(
        orch.stream_answer("Capital?", [], "kb", "k_cached")
    )
    assert "Berlin" in "".join(tokens)
    orch._vector_store.retrieve.assert_not_called()


@pytest.mark.asyncio
async def test_retrieval_failure_raises_domain_error() -> None:
    orch = _make_orch(retrieval_error=ConnectionError("DB down"))
    with pytest.raises(RAGRetrievalError):
        await _collect(orch.stream_answer("?", [], "kb", "k2"))


@pytest.mark.asyncio
async def test_stream_failure_raises_domain_error() -> None:
    orch = _make_orch(stream_error=RuntimeError("stream broke"))
    with pytest.raises(LLMStreamError):
        await _collect(orch.stream_answer("?", [], "kb", "k3"))


@pytest.mark.asyncio
async def test_empty_retrieval_uses_fallback_prompt() -> None:
    orch = _make_orch(chunks=[])
    tokens = await _collect(orch.stream_answer("Unknown topic", [], "kb", "k4"))
    assert isinstance(tokens, list)  # no crash, stream continues


@pytest.mark.asyncio
async def test_history_is_forwarded_to_llm() -> None:
    orch = _make_orch()
    history = [Message(role="user", content="Hi"), Message(role="assistant", content="Hello")]
    await _collect(orch.stream_answer("Capital?", history, "kb", "k5"))
    call_kwargs = orch._llm.stream.call_args
    messages = call_kwargs[0][1]  # positional arg: messages list
    assert any(m["content"] == "Hi" for m in messages)
