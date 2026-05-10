"""
Prompt templates for the RAG pipeline.
Centralizing prompts here makes them easy to iterate on.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    """Immutable prompt template with a simple .render() method."""

    system: str
    user_template: str  # supports {context} and {question} placeholders

    def render(self, context: str, question: str) -> str:
        return self.user_template.format(context=context, question=question)


# ── Default RAG prompt ─────────────────────────────────────────────────────────

RAG_PROMPT = PromptTemplate(
    system=(
        "You are a precise and helpful assistant. "
        "Answer the user's question using ONLY the provided context. "
        "If the answer is not in the context, say so honestly. "
        "Be concise and factual."
    ),
    user_template=(
        "Context information:
"
        "─────────────────────
"
        "{context}
"
        "─────────────────────

"
        "Question: {question}

"
        "Answer:"
    ),
)

# ── Fallback prompt (no context found) ────────────────────────────────────────

NO_CONTEXT_PROMPT = PromptTemplate(
    system="You are a helpful assistant.",
    user_template=(
        "No relevant context was found in the knowledge base.

"
        "Question: {question}

"
        "Answer as best you can from general knowledge:"
    ),
)
