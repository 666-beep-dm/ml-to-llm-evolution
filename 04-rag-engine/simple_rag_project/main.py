"""
Simple RAG (Retrieval-Augmented Generation) demo.
Finds the most semantically similar text from a knowledge base for a given query.
"""

import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --- Knowledge Base ---
KNOWLEDGE_BASE = [
    "Python is a high-level, interpreted programming language known for its simplicity.",
    "Machine learning is a subset of artificial intelligence focused on learning from data.",
    "Docker is a platform for developing and running applications in containers.",
    "PostgreSQL is a powerful open-source relational database management system.",
    "FastAPI is a modern, fast web framework for building APIs with Python.",
    "RAG stands for Retrieval-Augmented Generation and combines search with language models.",
    "Git is a distributed version control system for tracking changes in source code.",
    "Numpy is a Python library for numerical computing with support for large arrays.",
    "Redis is an in-memory data store used as a database, cache, and message broker.",
    "REST API is an architectural style for designing networked applications over HTTP.",
]

# Model name — can be overridden via environment variable
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# HuggingFace cache dir — set to mounted volume path in Docker
HF_CACHE_DIR = os.getenv("HF_HOME", None)


def load_model() -> SentenceTransformer:
    """Load the sentence embedding model from cache or download it."""
    print(f"Loading model: {MODEL_NAME} ...")
    if HF_CACHE_DIR:
        print(f"Using cache dir: {HF_CACHE_DIR}")
    return SentenceTransformer(MODEL_NAME, cache_folder=HF_CACHE_DIR)


def embed_texts(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    """Convert a list of strings into embedding vectors."""
    return model.encode(texts, convert_to_numpy=True)


def find_best_match(
    query: str,
    model: SentenceTransformer,
    kb_embeddings: np.ndarray,
) -> tuple[str, float]:
    """
    Find the knowledge base entry most similar to the query.

    Returns:
        Tuple of (best matching text, similarity score).
    """
    query_embedding = model.encode([query], convert_to_numpy=True)
    similarities = cosine_similarity(query_embedding, kb_embeddings)[0]
    best_idx = int(np.argmax(similarities))
    return KNOWLEDGE_BASE[best_idx], float(similarities[best_idx])


def main():
    model = load_model()
    kb_embeddings = embed_texts(model, KNOWLEDGE_BASE)
    print(f"Knowledge base loaded: {len(KNOWLEDGE_BASE)} entries.\n")

    print("=== Simple RAG Search ===")
    print("Type your query (or 'quit' to exit).\n")

    while True:
        try:
            query = input("Your query: ").strip()
        except EOFError:
            # Graceful exit if stdin is closed (e.g. in non-interactive Docker run)
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        best_text, score = find_best_match(query, model, kb_embeddings)
        print(f"\n[Best match — similarity: {score:.4f}]")
        print(f"  → {best_text}\n")


if __name__ == "__main__":
    main()
