"""Pure domain value objects."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    source: str
    score: float


@dataclass
class RAGContext:
    chunks: list[RetrievedChunk] = field(default_factory=list)
    retrieval_ms: float = 0.0

    @property
    def is_empty(self) -> bool:
        return not self.chunks

    def as_context_string(self) -> str:
        if self.is_empty:
            return ""
        sep = "\n\n---\n\n"
        parts = [
            f"[Source: {c.source}]\n{c.text}" for c in self.chunks
        ]
        return sep.join(parts)
