"""
Centralized, validated configuration.
Single Responsibility: owns all env-var parsing.
"""
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Service identity
    service_name: str = "senior-rag-production"
    environment: str = "production"

    # LLM
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1024
    temperature: float = 0.2

    # Embeddings & reranking
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Chunking
    chunk_size: int = Field(512, ge=128, le=4096)
    chunk_overlap: int = Field(64, ge=0, le=512)

    # Retrieval
    top_k: int = Field(10, ge=1, le=100)
    rerank_top_n: int = Field(3, ge=1, le=20)

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "documents"

    # Redis
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 3600
    embedding_cache_ttl: int = 86400

    # Observability
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("rerank_top_n")
    @classmethod
    def rerank_le_top_k(cls, v: int, info) -> int:
        top_k = info.data.get("top_k", 10)
        if v > top_k:
            raise ValueError(f"rerank_top_n ({v}) must be <= top_k ({top_k})")
        return v

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
