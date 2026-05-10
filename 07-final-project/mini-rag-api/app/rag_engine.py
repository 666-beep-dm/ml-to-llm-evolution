"""
RAG Engine: loads .txt files, splits them into chunks,
encodes with sentence-transformers, and retrieves via cosine similarity.
"""

import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

CHUNK_SIZE = 500
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class RAGEngine:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.model = SentenceTransformer(MODEL_NAME)
        self.chunks: list[str] = []
        self.embeddings: np.ndarray | None = None

    # ── Indexing ───────────────────────────────────────────────────────────────

    def _read_docs(self) -> list[str]:
        """Read all .txt files from docs_dir."""
        texts = []
        for path in sorted(self.docs_dir.glob("*.txt")):
            texts.append(path.read_text(encoding="utf-8"))
        return texts

    def _split_into_chunks(self, text: str) -> list[str]:
        """Split text into non-overlapping chunks of CHUNK_SIZE characters."""
        return [text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

    def load_and_index(self) -> None:
        """Load docs, chunk them, and pre-compute embeddings."""
        for text in self._read_docs():
            self.chunks.extend(self._split_into_chunks(text))

        if not self.chunks:
            raise RuntimeError(f"No .txt files found in {self.docs_dir}")

        print(f"[RAG] Indexed {len(self.chunks)} chunks from {self.docs_dir}")
        self.embeddings = self.model.encode(self.chunks, convert_to_numpy=True)

    # ── Retrieval ──────────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 1) -> str:
        """Return the most relevant chunk for the given query."""
        query_vec = self.model.encode([query], convert_to_numpy=True)
        scores = cosine_similarity(query_vec, self.embeddings)[0]
        best_idx = int(np.argmax(scores))
        return self.chunks[best_idx]
