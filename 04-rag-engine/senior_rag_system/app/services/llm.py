"""
LLM service — supports OpenAI and Anthropic.
Anti-hallucination system prompt is baked in here.
"""

from app.core.config import settings
from app.core.logging import logger

SYSTEM_PROMPT = """You are a precise, helpful assistant operating in a Retrieval-Augmented Generation (RAG) system.

Rules you must follow without exception:
1. Answer ONLY based on the provided context passages.
2. If the context does not contain sufficient information, respond with:
   "I cannot answer this question based on the available documents."
3. Never fabricate facts, citations, names, dates, or statistics.
4. If the question is ambiguous, state your interpretation before answering.
5. Keep answers concise and well-structured.
6. Always cite the source document(s) you relied on at the end of your answer.

Context passages will be prefixed with [SOURCE: <source_name>].
"""


def _build_user_message(question: str, context_chunks: list[dict]) -> str:
    parts: list[str] = ["### Context Passages
"]
    for i, chunk in enumerate(context_chunks, 1):
        parts.append(
            f"[{i}] [SOURCE: {chunk['source']}]
{chunk['content']}
"
        )
    parts.append(f"
### Question
{question}")
    return "
".join(parts)


def generate(question: str, context_chunks: list[dict]) -> str:
    """
    Generate a grounded answer using the configured LLM provider.

    Args:
        question:       User's natural language question.
        context_chunks: List of dicts with keys 'content' and 'source'.

    Returns:
        LLM-generated answer string.
    """
    user_message = _build_user_message(question, context_chunks)
    provider = settings.llm_provider.lower()

    logger.info("Calling LLM provider='{}' with {} context chunks",
                provider, len(context_chunks))

    if provider == "openai":
        return _call_openai(user_message)
    if provider == "anthropic":
        return _call_anthropic(user_message)

    raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Use 'openai' or 'anthropic'.")


def _call_openai(user_message: str) -> str:
    from openai import OpenAI

    if not settings.openai_api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=1024,
    )
    return response.choices[0].message.content or ""


def _call_anthropic(user_message: str) -> str:
    import anthropic

    if not settings.anthropic_api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set.")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text
