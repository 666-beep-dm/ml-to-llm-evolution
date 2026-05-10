"""DI container — wires all adapters and the domain orchestrator."""

import logging

from infra.adapters.redis_cache import RedisCache
from infra.adapters.chroma_store import ChromaVectorStore
from infra.adapters.openai_llm import OpenAILLM
from infra.adapters.rate_limiter import RateLimiterAdapter
from infra.config import settings
from internal.domain.rag_orchestrator import RAGOrchestrator

logger = logging.getLogger(__name__)


class Container:
    """Single-instance container; created once during lifespan startup."""

    def __init__(
        self,
        cache: RedisCache,
        vector_store: ChromaVectorStore,
        llm: OpenAILLM,
        rate_limiter: RateLimiterAdapter,
    ) -> None:
        self.cache = cache
        self.vector_store = vector_store
        self.llm = llm
        self.rate_limiter = rate_limiter
        self.settings = settings
        self.orchestrator = RAGOrchestrator(
            cache=cache,
            vector_store=vector_store,
            llm=llm,
            top_k=settings.rag_top_k,
            score_threshold=settings.rag_score_threshold,
            cache_ttl=settings.cache_ttl_seconds,
        )

    @classmethod
    async def create(cls) -> "Container":
        logger.info("container_init")
        cache = await RedisCache.create(settings.redis_url)
        vector_store = await ChromaVectorStore.create()
        llm = OpenAILLM()
        rate_limiter = RateLimiterAdapter()
        logger.info("container_ready")
        return cls(cache, vector_store, llm, rate_limiter)

    async def close(self) -> None:
        await self.cache.close()
        logger.info("container_closed")
