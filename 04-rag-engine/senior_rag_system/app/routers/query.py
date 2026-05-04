"""
/query router — RAG question-answering endpoint.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import QueryRequest, QueryResponse
from app.services import rag_pipeline
from app.core.logging import logger

router = APIRouter(prefix="/query", tags=["Query"])


@router.post(
    "",
    response_model=QueryResponse,
    summary="Ask a question and get a RAG-generated answer",
)
async def query_documents(request: QueryRequest) -> QueryResponse:
    try:
        return rag_pipeline.query(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Query pipeline failed: {}", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query error: {exc}",
        )
