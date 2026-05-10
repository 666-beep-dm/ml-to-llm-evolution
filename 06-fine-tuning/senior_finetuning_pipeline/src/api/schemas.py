"""src/api/schemas.py — Pydantic request/response schemas."""

from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class ModelVariant(str, Enum):
    base       = "base_model"
    fine_tuned = "fine_tuned"


class AskRequest(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=2000,
                              description="The user instruction or question.")
    model_variant: ModelVariant = Field(
        ModelVariant.fine_tuned,
        description="Which model to use: 'base_model' or 'fine_tuned'.",
    )
    max_new_tokens: int  = Field(256, ge=1,   le=1024)
    temperature:    float = Field(0.7, ge=0.01, le=2.0)
    top_p:          float = Field(0.9, ge=0.01, le=1.0)
    repetition_penalty: float = Field(1.1, ge=1.0, le=2.0)


class AskResponse(BaseModel):
    instruction:   str
    response:      str
    model_variant: str
    model_id:      str


class HealthResponse(BaseModel):
    status:     str
    cuda:       bool
    base_loaded:  bool
    lora_loaded:  bool


class MetricsResponse(BaseModel):
    base_perplexity:         float | None = None
    lora_perplexity:         float | None = None
    perplexity_delta:        float | None = None
    avg_cosine_similarity:   float | None = None
    test_samples:            int | None   = None
