"""
/ingest router — document ingestion endpoint.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import IngestRequest, IngestResponse
from app.services import rag_pipeline
from app.core.logging import logger

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post(
    "",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a document into the vector store",
)
async def ingest_document(request: IngestRequest) -> IngestResponse:
    try:
        return rag_pipeline.ingest(request)
    except Exception as exc:
        logger.exception("Ingestion failed: {}", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion error: {exc}",
        )
