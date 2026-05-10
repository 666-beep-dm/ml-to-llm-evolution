"""
Document ingestion pipeline: extract → chunk → return.
"""
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import get_settings
from app.core.exceptions import UnsupportedFileTypeError, ExtractionError
from app.core.logging import get_logger

logger = get_logger("doc_processor")

SUPPORTED = {".txt", ".pdf", ".md"}


def _extract_pdf(data: bytes) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "

".join(
                p.extract_text() or "" for p in pdf.pages
            )
    except ImportError:
        raise ExtractionError("pdfplumber not installed.")
    except Exception as exc:
        raise ExtractionError(f"PDF extraction failed: {exc}") from exc


def extract_text(filename: str, data: bytes) -> str:
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in SUPPORTED:
        raise UnsupportedFileTypeError(
            f"File type '{ext}' not supported. Allowed: {SUPPORTED}"
        )
    if ext == ".pdf":
        return _extract_pdf(data)
    return data.decode("utf-8", errors="replace")


def chunk_text(text: str) -> list[str]:
    s = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=s.chunk_size,
        chunk_overlap=s.chunk_overlap,
        separators=["

", "
", ". ", "! ", "? ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_text(text)
    logger.debug("doc.chunked", total=len(chunks), size=s.chunk_size)
    return [c.strip() for c in chunks if c.strip()]


def process_document(filename: str, data: bytes) -> list[str]:
    text = extract_text(filename, data)
    if not text.strip():
        raise ExtractionError(f"No text extracted from '{filename}'.")
    return chunk_text(text)
