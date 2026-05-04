"""
Ingestion pipeline:
  1. Load documents from /data
  2. Split into chunks (RecursiveCharacterTextSplitter)
  3. Embed with sentence-transformers
  4. Build and persist a FAISS vector index
"""

import logging
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import settings
from src.loader import load_documents

logger = logging.getLogger(__name__)


def get_embeddings() -> HuggingFaceEmbeddings:
    """Initialise the sentence-transformer embedding model."""
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        cache_folder=settings.hf_home,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_index() -> FAISS:
    """
    Full ingestion pipeline: load → split → embed → index.

    Returns:
        A FAISS vector store ready for similarity search.
    """
    # ── 1. Load ──────────────────────────────────────────────────────────────
    documents = load_documents(settings.data_dir)
    if not documents:
        raise ValueError(f"No documents found in '{settings.data_dir}'. Add .txt or .json files.")

    # ── 2. Split ─────────────────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info("Split into %d chunks (size=%d, overlap=%d)",
                len(chunks), settings.chunk_size, settings.chunk_overlap)

    # ── 3 & 4. Embed + Index ─────────────────────────────────────────────────
    embeddings = get_embeddings()
    logger.info("Building FAISS index …")
    index = FAISS.from_documents(chunks, embeddings)

    # ── Persist ──────────────────────────────────────────────────────────────
    Path(settings.faiss_index_path).mkdir(parents=True, exist_ok=True)
    index.save_local(settings.faiss_index_path)
    logger.info("FAISS index saved to '%s'", settings.faiss_index_path)

    return index


def load_index() -> FAISS:
    """Load an existing FAISS index from disk."""
    index_path = Path(settings.faiss_index_path)
    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at '{index_path}'. Run ingest first."
        )
    embeddings = get_embeddings()
    return FAISS.load_local(
        str(index_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def get_or_build_index() -> FAISS:
    """Return cached index if it exists, otherwise build from scratch."""
    try:
        index = load_index()
        logger.info("Loaded existing FAISS index from '%s'", settings.faiss_index_path)
        return index
    except (FileNotFoundError, RuntimeError):
        logger.info("No index found — building from documents …")
        return build_index()
