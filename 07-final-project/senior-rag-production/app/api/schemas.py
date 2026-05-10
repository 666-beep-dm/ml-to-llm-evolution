"""
Pydantic v2 request/response schemas. Pure data contracts, no logic.
"""
from pydantic import BaseModel, Field


class UploadResult(BaseModel):
    filename: str
    chunks_stored: int
    total_in_db: int
    message: str = "Document ingested successfully."


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4096)
    top_k: int | None = Field(None, ge=1, le=50)
    stream: bool = False
    prompt_name: str = "rag_default"


class SourceRef(BaseModel):
    source: str
    score: float


class AskResult(BaseModel):
    answer: str
    sources: list[SourceRef]
    context_used: bool
    latency_ms: int = 0


class HealthResult(BaseModel):
    status: str
    vector_store: str
    cache: str
    chunks_indexed: int
    version: str = "3.0.0"


class ErrorResponse(BaseModel):
    error_code: str
    detail: str
