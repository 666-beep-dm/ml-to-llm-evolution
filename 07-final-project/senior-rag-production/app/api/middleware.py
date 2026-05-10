"""
Request logging, metrics collection, and exception handling middleware.
"""
import time
import traceback
import uuid
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.core.exceptions import RAGException
from app.core.logging import get_logger
from app.api.routes.metrics import REQUEST_COUNT, REQUEST_LATENCY

logger = get_logger("http")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - t0

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(elapsed)

        logger.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            ms=round(elapsed * 1000, 1),
        )
        response.headers["X-Request-ID"] = request_id
        return response


# ── Exception handlers ────────────────────────────────────────────────────────

async def rag_exception_handler(request: Request, exc: RAGException):
    logger.warning("domain.error", code=exc.error_code, detail=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "detail": str(exc)},
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled.exception",
        path=request.url.path,
        exc=str(exc),
        trace=traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error_code": "INTERNAL_ERROR", "detail": "Unexpected error. Check logs."},
    )
