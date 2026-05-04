"""
Central configuration — all values come from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── LLM provider ──────────────────────────────────────────────────────────
    # "openai" | "ollama"
    llm_provider: str = Field("ollama", alias="LLM_PROVIDER")

    # OpenAI
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")

    # Ollama
    ollama_base_url: str = Field("http://ollama:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field("llama3.2", alias="OLLAMA_MODEL")

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = Field(
        "all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )
    hf_home: str = Field("/hf_cache", alias="HF_HOME")

    # ── FAISS index ───────────────────────────────────────────────────────────
    faiss_index_path: str = Field("/app/faiss_index", alias="FAISS_INDEX_PATH")

    # ── Documents ─────────────────────────────────────────────────────────────
    data_dir: str = Field("/app/data", alias="DATA_DIR")

    # ── Chunking ──────────────────────────────────────────────────────────────
    chunk_size: int = Field(512, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(64, alias="CHUNK_OVERLAP")

    # ── Retrieval ─────────────────────────────────────────────────────────────
    top_k: int = Field(3, alias="TOP_K")

    model_config = {"env_file": ".env", "populate_by_name": True}


# Singleton — import this everywhere
settings = Settings()
