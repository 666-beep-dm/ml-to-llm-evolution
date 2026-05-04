"""
Retriever — wraps FAISS similarity search.
Returns the top-k most relevant chunks for a given query.
"""

import logging

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.config import settings

logger = logging.getLogger(__name__)


def retrieve(query: str, index: FAISS) -> list[Document]:
    """
    Perform similarity search against the FAISS index.

    Args:
        query:  User's natural language question.
        index:  Loaded FAISS vector store.

    Returns:
        Top-k Document chunks ordered by relevance (most relevant first).
    """
    if not query.strip():
        raise ValueError("Query must not be empty.")

    results = index.similarity_search(query, k=settings.top_k)
    logger.info("Retrieved %d chunks for query: '%s'", len(results), query[:80])
    return results
