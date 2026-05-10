"""LLM service — all OpenAI interaction lives here."""

import logging

from openai import AsyncOpenAI, APITimeoutError, RateLimitError, APIStatusError

from app.core.config import settings
from app.schemas.chat import AskRequest, AskResponse, Message
from app.services.exceptions import (
    LLMTimeoutError,
    LLMRateLimitError,
    LLMEmptyResponseError,
    LLMAPIError,
)

logger = logging.getLogger(__name__)

_DEFAULT_SYSTEM = (
    "You are a helpful, concise, and professional assistant. "
    "Answer in the same language the user writes in."
)


class LLMService:
    """Wraps AsyncOpenAI and translates domain errors into service exceptions."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.timeout,
        )

    def _build_messages(self, request: AskRequest) -> list[dict[str, str]]:
        """Assemble the full message list sent to the model."""
        system_text = request.system_prompt or _DEFAULT_SYSTEM
        messages: list[dict[str, str]] = [{"role": "system", "content": system_text}]

        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": request.question})
        return messages

    async def ask(self, request: AskRequest) -> AskResponse:
        """
        Send the request to the LLM and return a structured response.

        Raises:
            LLMTimeoutError: When the API call exceeds the configured timeout.
            LLMRateLimitError: When OpenAI rate limits are hit.
            LLMEmptyResponseError: When the model returns no content.
            LLMAPIError: For any other OpenAI API error.
        """
        messages = self._build_messages(request)
        logger.info(
            "Sending request to model=%s turns=%d",
            settings.model_name,
            len(messages),
        )

        try:
            completion = await self._client.chat.completions.create(
                model=settings.model_name,
                messages=messages,  # type: ignore[arg-type]
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
            )
        except APITimeoutError as exc:
            logger.warning("OpenAI request timed out: %s", exc)
            raise LLMTimeoutError(timeout=settings.timeout) from exc
        except RateLimitError as exc:
            logger.warning("OpenAI rate limit hit: %s", exc)
            raise LLMRateLimitError() from exc
        except APIStatusError as exc:
            logger.error("OpenAI API error status=%s: %s", exc.status_code, exc)
            raise LLMAPIError(status_code=exc.status_code, message=str(exc)) from exc

        choice = completion.choices[0]
        answer = choice.message.content

        if not answer or not answer.strip():
            logger.error("Model returned an empty response.")
            raise LLMEmptyResponseError()

        usage = completion.usage
        logger.info(
            "Response received prompt_tokens=%d completion_tokens=%d",
            usage.prompt_tokens if usage else 0,
            usage.completion_tokens if usage else 0,
        )

        return AskResponse(
            answer=answer.strip(),
            model=completion.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
        )
