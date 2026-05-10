"""
ChromaDB-backed vector store with a clean interface.
The collection is persisted under ./vector_db/.
"""

import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings
from app.core.logging import logger
from app.services.embeddings import embedding_service


class VectorStore:
    _instance: "VectorStore | None" = None

    def __new__(cls) -> "VectorStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def init(self) -> None:
        if self._initialized:
            return
        settings = get_settings()
        db_path = Path(settings.vector_db_path)
        db_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing ChromaDB at {db_path}")
        self._client = chromadb.PersistentClient(
            path=str(db_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._initialized = True
        logger.info(
            f"Vector store ready — collection '{settings.collection_name}' "
            f"has {self._collection.count()} chunks."
        )

    # ── Write ─────────────────────────────────────────────────────────────────

    def add_chunks(self, chunks: list[str], source: str) -> int:
        """Embed and store chunks. Returns number of chunks stored."""
        if not chunks:
            return 0
        embeddings = embedding_service.encode(chunks)
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"source": source, "chunk_index": i} for i, _ in enumerate(chunks)]

        self._collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )
        logger.info(f"Stored {len(chunks)} chunks from source='{source}'")
        return len(chunks)

    # ── Read ──────────────────────────────────────────────────────────────────

    def query(self, question: str, top_k: int | None = None) -> list[dict]:
        """Return top-k most relevant chunks with metadata and distance."""
        k = top_k or get_settings().top_k
        query_embedding = embedding_service.encode_one(question)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, max(self._collection.count(), 1)),
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append({"text": doc, "source": meta.get("source", ""), "score": 1 - dist})
        return hits

    @property
    def count(self) -> int:
        return self._collection.count()


vector_store = VectorStore()
