"""
Orchestrates the full RAG pipeline:
  upload → process → store
  ask    → retrieve → prompt → generate
"""

from app.services.document_processor import process_document
from app.services.vector_store import vector_store
from app.services.llm_client import chat_completion
from app.core.prompts import RAG_PROMPT, NO_CONTEXT_PROMPT
from app.core.config import get_settings
from app.core.logging import logger


async def ingest_document(filename: str, raw_bytes: bytes) -> dict:
    """Process a document and store its chunks. Returns ingestion summary."""
    chunks = process_document(filename, raw_bytes)
    count = vector_store.add_chunks(chunks, source=filename)
    logger.info(f"Ingested '{filename}': {count} chunks stored.")
    return {"filename": filename, "chunks_stored": count, "total_in_db": vector_store.count}


async def answer_question(question: str) -> dict:
    """Retrieve context and generate an LLM answer."""
    settings = get_settings()
    hits = vector_store.query(question, top_k=settings.top_k)

    if hits:
        context_parts = [
            f"[{i+1}] (source: {h['source']}, score: {h['score']:.3f})\n{h['text']}"
            for i, h in enumerate(hits)
        ]
        context = "\n\n".join(context_parts)
        prompt = RAG_PROMPT
    else:
        context = ""
        prompt = NO_CONTEXT_PROMPT
        logger.warning("No relevant chunks found — falling back to LLM without context.")

    user_message = prompt.render(context=context, question=question)
    answer = await chat_completion(system=prompt.system, user=user_message)

    return {
        "answer": answer,
        "sources": [{"source": h["source"], "score": round(h["score"], 4)} for h in hits],
        "context_used": bool(hits),
    }
