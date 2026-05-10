"""
API route definitions for /upload and /ask.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.api.schemas import UploadResponse, AskRequest, AskResponse
from app.services.rag_service import ingest_document, answer_question
from app.core.logging import logger

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt", ".pdf"}
MAX_FILE_SIZE_MB = 20


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a .txt or .pdf file. The service will chunk it and store embeddings.",
)
async def upload_document(file: UploadFile = File(...)):
    # ── Validate extension ─────────────────────────────────────────────────────
    filename = file.filename or "unknown"
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{suffix}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    # ── Read & size-check ──────────────────────────────────────────────────────
    raw_bytes = await file.read()
    size_mb = len(raw_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({size_mb:.1f} MB). Max: {MAX_FILE_SIZE_MB} MB.",
        )

    logger.info(f"Uploading file: {filename} ({size_mb:.2f} MB)")

    result = await ingest_document(filename, raw_bytes)
    return UploadResponse(**result)


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question",
    description="Ask a question against the indexed knowledge base.",
)
async def ask_question(payload: AskRequest):
    logger.info(f"Question received: {payload.question[:80]}...")
    result = await answer_question(payload.question)
    return AskResponse(**result)
