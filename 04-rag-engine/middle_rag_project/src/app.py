"""
RAG application entry point.
  1. Builds or loads the FAISS index.
  2. Enters an interactive Q&A loop.
  3. For each query: retrieve top-k chunks → call LLM → print answer.
"""

import logging
import sys

from src.ingest import get_or_build_index
from src.retriever import retrieve
from src.llm import generate_answer
from src.config import settings

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run() -> None:
    """Main application loop."""
    logger.info("Starting RAG pipeline …")
    logger.info(
        "Config: provider=%s | embed=%s | top_k=%d | chunk=%d/%d",
        settings.llm_provider,
        settings.embedding_model,
        settings.top_k,
        settings.chunk_size,
        settings.chunk_overlap,
    )

    # Build or load vector index
    try:
        index = get_or_build_index()
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Failed to initialise index: %s", exc)
        sys.exit(1)

    print("\n" + "═" * 60)
    print("  RAG Assistant — type 'quit' to exit")
    print("═" * 60 + "\n")

    while True:
        try:
            query = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # ── Retrieve ─────────────────────────────────────────────────────────
        try:
            chunks = retrieve(query, index)
        except ValueError as exc:
            print(f"[Error] {exc}\n")
            continue

        # ── Show retrieved context ────────────────────────────────────────────
        print(f"\n── Retrieved {len(chunks)} chunk(s) ──")
        for i, doc in enumerate(chunks, 1):
            source = doc.metadata.get("source", "unknown")
            preview = doc.page_content[:120].replace("\n", " ")
            print(f"  [{i}] {source}  →  {preview}…")

        # ── Generate answer ───────────────────────────────────────────────────
        context_texts = [doc.page_content for doc in chunks]
        try:
            answer = generate_answer(query, context_texts)
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            print(f"[Error] LLM unavailable: {exc}\n")
            continue

        print(f"\n── Answer ──\n{answer}\n")
        print("─" * 60 + "\n")


if __name__ == "__main__":
    run()
