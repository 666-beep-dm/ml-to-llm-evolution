"""
Async LLM client with streaming support.
Uses httpx for async requests; compatible with OpenAI and Ollama.
"""
from __future__ import annotations
import json
from typing import AsyncIterator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger("llm")
TIMEOUT = httpx.Timeout(120.0, connect=10.0)


def _build_headers() -> dict[str, str]:
    s = get_settings()
    h = {"Content-Type": "application/json"}
    if s.openai_api_key:
        h["Authorization"] = f"Bearer {s.openai_api_key}"
    return h


def _build_payload(system: str, user: str, stream: bool) -> dict:
    s = get_settings()
    return {
        "model": s.model_name,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": s.temperature,
        "max_tokens": s.max_tokens,
        "stream": stream,
    }


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def chat(system: str, user: str) -> str:
    """Non-streaming completion."""
    url = get_settings().openai_base_url.rstrip("/") + "/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                url, json=_build_payload(system, user, stream=False),
                headers=_build_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as exc:
        raise LLMError(f"LLM HTTP {exc.response.status_code}: {exc.response.text}") from exc
    except Exception as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc


async def chat_stream(system: str, user: str) -> AsyncIterator[str]:
    """Streaming completion — yields text deltas."""
    url = get_settings().openai_base_url.rstrip("/") + "/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async with client.stream(
                "POST", url,
                json=_build_payload(system, user, stream=True),
                headers=_build_headers(),
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:]
                    if payload.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(payload)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError):
                        continue
    except httpx.HTTPStatusError as exc:
        raise LLMError(f"Stream HTTP {exc.response.status_code}") from exc
    except Exception as exc:
        raise LLMError(f"Stream failed: {exc}") from exc
