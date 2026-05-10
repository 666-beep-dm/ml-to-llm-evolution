"""HTTP-layer request / response schemas (Pydantic v2)."""

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., examples=["user"])
    content: str = Field(..., min_length=1)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4096)
    history: list[Message] = Field(default_factory=list)
    collection: str = Field(default="knowledge_base")
    system_prompt: str | None = None


class AskResponse(BaseModel):
    answer: str
    model: str
    sources: list[str] = Field(default_factory=list)
    cached: bool = False
    retrieval_ms: float = 0.0
    generation_ms: float = 0.0


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
