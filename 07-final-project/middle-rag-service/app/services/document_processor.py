"""
Document ingestion: extract text from .txt / .pdf, split into chunks.
Uses LangChain's RecursiveCharacterTextSplitter.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import get_settings
from app.core.logging import logger


def extract_text(filename: str, raw_bytes: bytes) -> str:
    """Extract plain text from .txt or .pdf bytes."""
    if filename.endswith(".pdf"):
        try:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                return "\n".join(
                    page.extract_text() or "" for page in pdf.pages
                )
        except ImportError:
            raise RuntimeError(
                "pdfplumber is required for PDF support. "
                "Add it to requirements.txt."
            )
    # Default: treat as UTF-8 text
    return raw_bytes.decode("utf-8", errors="replace")


def split_text(text: str) -> list[str]:
    """Split text into overlapping chunks using RecursiveCharacterTextSplitter."""
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    logger.debug(f"Split text into {len(chunks)} chunks "
                 f"(size={settings.chunk_size}, overlap={settings.chunk_overlap})")
    return chunks


def process_document(filename: str, raw_bytes: bytes) -> list[str]:
    """Full pipeline: extract → split."""
    text = extract_text(filename, raw_bytes)
    if not text.strip():
        raise ValueError(f"No text could be extracted from '{filename}'.")
    return split_text(text)
