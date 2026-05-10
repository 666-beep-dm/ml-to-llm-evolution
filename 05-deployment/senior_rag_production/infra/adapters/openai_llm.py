"""OpenAI streaming LLM adapter."""

import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI, APITimeoutError, RateLimitError, APIStatusError

from infra.config import settings
from internal.domain.exceptions import LLMStreamError, RateLimitedError

logger = logging.getLogger(__name__)


class OpenAILLM:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.streaming_timeout,
        )

    async def stream(
        self,
        system: str,
        messages: list[dict[str, str]],
    ) -> AsyncGenerator[str, None]:
        all_messages = [{"role": "system", "content": system}, *messages]
        try:
            async with self._client.chat.completions.stream(
                model=settings.model_name,
                messages=all_messages,  # type: ignore[arg-type]
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
            ) as stream_ctx:
                async for event in stream_ctx:
                    delta = (
                        event.choices[0].delta.content
                        if event.choices
                        else None
                    )
                    if delta:
                        yield delta
        except RateLimitError as exc:
            raise RateLimitedError("OpenAI rate limit exceeded.") from exc
        except APITimeoutError as exc:
            raise LLMStreamError(
                f"Stream timed out after {settings.streaming_timeout}s."
            ) from exc
        except APIStatusError as exc:
            raise LLMStreamError(
                f"OpenAI API error {exc.status_code}."
            ) from exc
        except Exception as exc:
            raise LLMStreamError(f"Unexpected stream error: {exc}") from exc
