"""API router — thin controller layer."""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas.chat import AskRequest, AskResponse, ErrorResponse
from app.services.exceptions import LLMServiceError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/ask",
    response_model=AskResponse,
    responses={
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        504: {"model": ErrorResponse, "description": "LLM timeout"},
        502: {"model": ErrorResponse, "description": "LLM API error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Ask a question (with optional conversation history)",
)
async def ask(request: Request, payload: AskRequest) -> AskResponse | JSONResponse:
    """
    Send a question to the configured LLM model.

    - **question**: The new user message.
    - **history**: Previous conversation turns (oldest first).
    - **system_prompt**: Optional override for the system instruction.
    """
    llm_service = request.app.state.llm_service
    try:
        return await llm_service.ask(payload)
    except LLMServiceError as exc:
        logger.warning("LLM service error: %s", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=type(exc).__name__,
                detail=exc.user_message,
            ).model_dump(),
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled exception in /ask: %s", exc)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="InternalServerError",
                detail="An unexpected error occurred.",
            ).model_dump(),
        )
