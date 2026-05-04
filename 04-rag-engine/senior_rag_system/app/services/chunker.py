"""
Text chunking service.
Uses LangChain RecursiveCharacterTextSplitter as the primary strategy.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings


def split(text: str) -> list[str]:
    """Split *text* into overlapping chunks ready for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]
