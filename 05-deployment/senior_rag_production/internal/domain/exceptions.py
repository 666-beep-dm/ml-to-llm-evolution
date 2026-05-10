"""Domain exceptions — framework-free."""


class DomainError(Exception):
    """Base domain error."""


class RAGRetrievalError(DomainError):
    """Vector DB unavailable or retrieval failed."""


class LLMStreamError(DomainError):
    """LLM stream interrupted or returned an error."""


class RateLimitedError(DomainError):
    """Client exceeded the rate limit."""


class CacheError(DomainError):
    """Cache read/write failure (non-fatal)."""


class EmbeddingError(DomainError):
    """Failed to generate vector embeddings."""
