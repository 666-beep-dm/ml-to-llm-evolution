"""Request / response schemas for the chat API."""

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single chat turn."""

    role: str = Field(
        ...,
        description="One of: 'user', 'assistant', 'system'",
        examples=["user"],
    )
    content: str = Field(..., min_length=1, examples=["Hello!"])


class AskRequest(BaseModel):
    """Payload for POST /ask."""

    question: str = Field(..., min_length=1, description="The new user question.")
    history: list[Message] = Field(
        default_factory=list,
        description="Previous conversation turns (oldest first).",
    )
    system_prompt: str | None = Field(
        default=None,
        description="Optional system-level instruction for the model.",
    )


class AskResponse(BaseModel):
    """Successful response from POST /ask."""

    answer: str
    model: str
    prompt_tokens: int
    completion_tokens: int


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    error: str
    detail: str | None = None
