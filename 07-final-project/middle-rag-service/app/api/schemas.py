"""
Pydantic v2 request / response schemas.
"""

from pydantic import BaseModel, Field


# ── /upload ───────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    filename: str
    chunks_stored: int
    total_in_db: int
    message: str = "Document ingested successfully."


# ── /ask ──────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class SourceReference(BaseModel):
    source: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    context_used: bool


# ── Error ─────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
