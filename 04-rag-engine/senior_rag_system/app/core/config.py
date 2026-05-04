"""
Central configuration via pydantic-settings.
All values are read from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────────────────────
    app_name: str = Field("Senior RAG System", alias="APP_NAME")
    debug: bool = Field(False, alias="DEBUG")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    # ── LLM ───────────────────────────────────────────────────────────────────
    # "openai" | "anthropic"
    llm_provider: str = Field("openai", alias="LLM_PROVIDER")
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")
    anthropic_api_key: str = Field("", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field("claude-sonnet-4-5", alias="ANTHROPIC_MODEL")

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = Field("all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    hf_home: str = Field("/hf_cache", alias="HF_HOME")

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chroma_host: str = Field("chroma", alias="CHROMA_HOST")
    chroma_port: int = Field(8000, alias="CHROMA_PORT")
    chroma_collection: str = Field("rag_documents", alias="CHROMA_COLLECTION")

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = Field("redis://redis:6379/0", alias="REDIS_URL")
    cache_ttl_seconds: int = Field(3600, alias="CACHE_TTL_SECONDS")
    # Cosine distance threshold for semantic cache hit (lower = stricter)
    cache_similarity_threshold: float = Field(0.15, alias="CACHE_SIMILARITY_THRESHOLD")

    # ── Chunking ──────────────────────────────────────────────────────────────
    chunk_size: int = Field(512, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(64, alias="CHUNK_OVERLAP")

    # ── Retrieval ─────────────────────────────────────────────────────────────
    top_k: int = Field(5, alias="TOP_K")
    rerank_top_n: int = Field(3, alias="RERANK_TOP_N")
    reranker_model: str = Field(
        "cross-encoder/ms-marco-MiniLM-L-6-v2", alias="RERANKER_MODEL"
    )

    model_config = {"env_file": ".env", "populate_by_name": True}


settings = Settings()
