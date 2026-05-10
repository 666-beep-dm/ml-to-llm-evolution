"""
Async LLM client using httpx.
Supports OpenAI-compatible APIs (OpenAI, Ollama, LocalAI, etc.).
"""

import httpx
from app.core.config import get_settings
from app.core.logging import logger

TIMEOUT = httpx.Timeout(60.0, connect=10.0)


async def chat_completion(system: str, user: str) -> str:
    """
    Send a chat completion request and return the assistant's reply.
    Compatible with any OpenAI-format endpoint.
    """
    settings = get_settings()

    headers = {"Content-Type": "application/json"}
    if settings.openai_api_key:
        headers["Authorization"] = f"Bearer {settings.openai_api_key}"

    payload = {
        "model": settings.model_name,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    logger.debug(f"LLM request → model={settings.model_name}, url={url}")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    answer = data["choices"][0]["message"]["content"].strip()
    logger.debug(f"LLM response received ({len(answer)} chars)")
    return answer
