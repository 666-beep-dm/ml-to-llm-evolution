"""
Custom middleware and exception handlers.
"""

import time
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status code, and duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} ({duration_ms:.1f}ms)"
        )
        return response


# ── Exception handlers ─────────────────────────────────────────────────────────

async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"ValueError on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "detail": str(exc)},
    )


async def runtime_error_handler(request: Request, exc: RuntimeError):
    logger.error(f"RuntimeError on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )


async def generic_error_handler(request: Request, exc: Exception):
    logger.critical(
        f"Unhandled exception on {request.url.path}:\n"
        + traceback.format_exc()
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Unexpected error", "detail": "Please check server logs."},
    )
