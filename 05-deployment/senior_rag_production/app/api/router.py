"""HTTP interface — thin controllers, SSE streaming."""

import hashlib
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from slowapi.util import get_remote_address

from app.schemas.chat import AskRequest, ErrorResponse
from internal.domain.rag_orchestrator import RAGOrchestrator
from internal.domain.exceptions import RAGRetrievalError, LLMStreamError

logger = logging.getLogger(__name__)
router = APIRouter()

_SSE_DONE = b"data: [DONE]\n\n"
_SSE_ERR_GENERIC = b"data: [ERROR] Internal stream failure\n\n"


def _get_orchestrator(request: Request) -> RAGOrchestrator:
    return request.app.state.container.orchestrator


def _sse(token: str) -> bytes:
    return ("data: " + token + "\n\n").encode()


def _sse_err(msg: str) -> bytes:
    return ("data: [ERROR] " + msg + "\n\n").encode()


async def _sse_error_body(
    status: int, error: str, detail: str
) -> AsyncGenerator[bytes, None]:
    yield _sse_err(detail)
    yield _SSE_DONE


@router.post(
    "/ask",
    response_model=None,
    summary="Streaming RAG answer (SSE)",
    responses={
        200: {"description": "Server-Sent Events token stream"},
        422: {"description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        503: {"model": ErrorResponse, "description": "Upstream service unavailable"},
    },
)
async def ask(
    request: Request,
    payload: AskRequest,
    orchestrator: RAGOrchestrator = Depends(_get_orchestrator),
) -> StreamingResponse:
    cache_key = hashlib.sha256(
        f"{payload.question}::{payload.collection}".encode()
    ).hexdigest()

    logger.info(
        "ask_request",
        extra={
            "client_ip": get_remote_address(request),
            "question_len": len(payload.question),
            "cache_key": cache_key[:12],
        },
    )

    try:
        stream = orchestrator.stream_answer(
            question=payload.question,
            history=payload.history,
            collection=payload.collection,
            cache_key=cache_key,
        )
        return StreamingResponse(
            _sse_wrapper(stream),
            media_type="text/event-stream",
            headers={
                "X-Cache-Key": cache_key[:12],
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    except RAGRetrievalError as exc:
        logger.warning("retrieval_error", extra={"detail": str(exc)})
        return StreamingResponse(
            _sse_error_body(503, "RAGRetrievalError", str(exc)),
            media_type="text/event-stream",
            status_code=503,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("unhandled_ask_error", extra={"error": str(exc)})
        return StreamingResponse(
            _sse_error_body(500, "InternalError", "Unexpected server error."),
            media_type="text/event-stream",
            status_code=500,
        )


async def _sse_wrapper(
    stream: AsyncGenerator[str, None],
) -> AsyncGenerator[bytes, None]:
    """Wrap token stream in SSE bytes; emit [DONE] or [ERROR] sentinel."""
    try:
        async for token in stream:
            yield _sse(token)
        yield _SSE_DONE
    except LLMStreamError as exc:
        logger.error("stream_interrupted", extra={"error": str(exc)})
        yield _sse_err(str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.exception("stream_crash", extra={"error": str(exc)})
        yield _SSE_ERR_GENERIC


@router.get("/health", summary="Liveness + dependency probe")
async def health(request: Request) -> dict[str, str]:
    container = request.app.state.container
    return {
        "status": "ok",
        "model": container.settings.model_name,
        "redis": await container.cache.ping(),
        "vector_db": await container.vector_store.ping(),
    }
