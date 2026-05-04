"""
LLM abstraction layer.
Supports two providers selected via LLM_PROVIDER env var:
  - "openai"  → OpenAI Chat API  (requires OPENAI_API_KEY)
  - "ollama"  → local Ollama server (default)
"""

import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import settings

logger = logging.getLogger(__name__)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Answer the user's question using ONLY the provided context. "
    "If the context does not contain enough information, say so honestly. "
    "Be concise and factual."
)


def get_llm() -> BaseChatModel:
    """Instantiate the configured LLM client."""
    provider = settings.llm_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in .env")
        from langchain_openai import ChatOpenAI
        logger.info("Using OpenAI model: %s", settings.openai_model)
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        logger.info(
            "Using Ollama model: %s @ %s",
            settings.ollama_model,
            settings.ollama_base_url,
        )
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. Choose 'openai' or 'ollama'."
    )


def generate_answer(query: str, context_chunks: list[str]) -> str:
    """
    Build a RAG prompt and call the LLM.

    Args:
        query:          User's question.
        context_chunks: List of retrieved text chunks.

    Returns:
        LLM-generated answer as a plain string.
    """
    context = "\n\n---\n\n".join(context_chunks)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    logger.info("Calling LLM (%s) …", settings.llm_provider)
    response = llm.invoke(messages)
    return response.content
