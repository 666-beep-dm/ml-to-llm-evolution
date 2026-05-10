"""POST /upload — document ingestion endpoint."""
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.api.deps import get_rag_service
from app.api.schemas import UploadResult
from app.core.exceptions import FileTooLargeError
from app.services.rag_service import RAGService
import json

router = APIRouter()
MAX_MB = 50


@router.post("/upload", response_model=UploadResult, status_code=status.HTTP_201_CREATED,
             summary="Ingest a document (.txt, .pdf, .md)")
async def upload(
    file: UploadFile = File(...),
    metadata: str | None = Form(None, description="Optional JSON metadata string"),
    rag: RAGService = Depends(get_rag_service),
) -> UploadResult:
    data = await file.read()
    if len(data) > MAX_MB * 1024 * 1024:
        raise FileTooLargeError(f"File exceeds {MAX_MB}MB limit.")

    meta = json.loads(metadata) if metadata else {}
    return await rag.ingest(file.filename or "unknown", data, meta)
