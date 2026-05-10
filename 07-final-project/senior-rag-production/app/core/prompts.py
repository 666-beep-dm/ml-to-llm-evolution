"""
Prompt Engine: manages system prompts and context assembly strategies.
Open/Closed: new strategies implement ContextStrategy without touching core.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol


# ── Context assembly strategies ───────────────────────────────────────────────

class ContextStrategy(Protocol):
    """Interface for context assembly strategies."""
    def assemble(self, hits: list[dict]) -> str: ...


@dataclass
class NumberedContextStrategy:
    """Numbered list with source attribution and relevance score."""
    max_chars: int = 6000

    def assemble(self, hits: list[dict]) -> str:
        parts, total = [], 0
        for i, h in enumerate(hits, 1):
            block = (
                f"[{i}] Source: {h.get('source', 'unknown')} "
                f"| Score: {h.get('score', 0):.3f}
"
                f"{h['text']}"
            )
            if total + len(block) > self.max_chars:
                break
            parts.append(block)
            total += len(block)
        return "

".join(parts)


@dataclass
class DenseContextStrategy:
    """Concatenated context for models with large context windows."""
    separator: str = "
---
"

    def assemble(self, hits: list[dict]) -> str:
        return self.separator.join(h["text"] for h in hits)


# ── Prompt Templates ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SystemPrompt:
    name: str
    system: str
    user_template: str
    context_strategy: ContextStrategy = field(
        default_factory=NumberedContextStrategy, compare=False
    )

    def render(self, question: str, hits: list[dict]) -> tuple[str, str]:
        """Returns (system_message, user_message)."""
        context = self.context_strategy.assemble(hits)
        user = self.user_template.format(context=context, question=question)
        return self.system, user


class PromptRegistry:
    """Registry of available prompt templates. Extensible without modification."""
    _registry: dict[str, SystemPrompt] = {}

    @classmethod
    def register(cls, prompt: SystemPrompt) -> None:
        cls._registry[prompt.name] = prompt

    @classmethod
    def get(cls, name: str) -> SystemPrompt:
        if name not in cls._registry:
            raise KeyError(f"Prompt '{name}' not registered. Available: {list(cls._registry)}")
        return cls._registry[name]

    @classmethod
    def list_names(cls) -> list[str]:
        return list(cls._registry.keys())


# ── Built-in prompts ──────────────────────────────────────────────────────────

PromptRegistry.register(SystemPrompt(
    name="rag_default",
    system=(
        "You are a precise, helpful AI assistant. "
        "Answer questions using ONLY the provided context. "
        "If the context does not contain the answer, clearly state that. "
        "Always cite the source numbers [1], [2] etc. when referring to context."
    ),
    user_template=(
        "Context:
{context}

"
        "Question: {question}

"
        "Answer (cite sources):"
    ),
))

PromptRegistry.register(SystemPrompt(
    name="rag_concise",
    system=(
        "You are a concise assistant. "
        "Answer in 1-3 sentences using ONLY the provided context."
    ),
    user_template="Context:
{context}

Question: {question}

Brief answer:",
))

PromptRegistry.register(SystemPrompt(
    name="rag_no_context",
    system="You are a helpful assistant. Answer from general knowledge.",
    user_template="Question: {question}

Answer:",
    context_strategy=DenseContextStrategy(),
))
