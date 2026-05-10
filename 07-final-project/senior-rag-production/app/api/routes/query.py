"""POST /ask — query endpoint with optional streaming."""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.api.deps import get_rag_service
from app.api.schemas import AskRequest, AskResult
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/ask", response_model=AskResult, summary="Ask a question (streaming optional)")
async def ask(payload: AskRequest, rag: RAGService = Depends(get_rag_service)):
    if payload.stream:
        async def _event_stream():
            async for delta in rag.answer_stream(payload.question, payload.prompt_name):
                yield f"data: {json.dumps({"delta": delta})}

"
            yield "data: [DONE]

"
        return StreamingResponse(_event_stream(), media_type="text/event-stream")

    return await rag.answer(payload.question, payload.prompt_name)
