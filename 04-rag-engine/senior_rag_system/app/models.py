"""
Pydantic request / response models.
These are the public contracts of the API — keep them stable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ── Ingest ────────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Payload for /ingest endpoint."""
    content: str = Field(..., min_length=1, description="Raw document text")
    source: str = Field(..., description="Origin of the document, e.g. URL or filename")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary extra metadata")


class IngestResponse(BaseModel):
    document_id: UUID
    chunks_stored: int
    source: str
    ingested_at: datetime


# ── Query ─────────────────────────────────────────────────────────────────────

class MetadataFilter(BaseModel):
    """Optional metadata filter applied before vector search."""
    key: str
    value: str | int | float | bool


class QueryRequest(BaseModel):
    """Payload for /query endpoint."""
    question: str = Field(..., min_length=3)
    top_k: int | None = Field(None, ge=1, le=20)
    filters: list[MetadataFilter] = Field(default_factory=list)
    use_cache: bool = Field(True, description="Allow semantic cache lookup")


class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    source: str
    document_id: str
    score: float
    rerank_score: float | None = None


class QueryResponse(BaseModel):
    answer: str
    chunks_used: list[RetrievedChunk]
    cached: bool = False
    latency_ms: float


# ── Health ────────────────────────────────────────────────────────────────────

class ComponentStatus(BaseModel):
    status: str          # "ok" | "degraded" | "down"
    detail: str = ""


class HealthResponse(BaseModel):
    status: str
    components: dict[str, ComponentStatus]
    version: str = "1.0.0"
