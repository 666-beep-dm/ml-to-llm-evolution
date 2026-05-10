"""pydantic-settings application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    log_level: str = "INFO"

    # OpenAI
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1024
    streaming_timeout: float = 60.0
    embedding_model: str = "text-embedding-3-small"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 3600
    rate_limit_requests: int = 20
    rate_limit_window_seconds: int = 60

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "knowledge_base"

    # RAG
    rag_top_k: int = 4
    rag_score_threshold: float = 0.35

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()  # type: ignore[call-arg]
