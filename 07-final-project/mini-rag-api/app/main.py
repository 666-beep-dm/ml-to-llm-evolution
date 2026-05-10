"""
Mini-RAG API – main entry point.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from app.rag_engine import RAGEngine
import openai
import os

# ── Lifespan: load documents once at startup ───────────────────────────────────

rag: RAGEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag
    rag = RAGEngine(docs_dir="docs")
    rag.load_and_index()
    yield


app = FastAPI(
    title="Mini-RAG API",
    description="A minimal Retrieval-Augmented Generation API built with FastAPI.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Schemas ────────────────────────────────────────────────────────────────────


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    context: str


# ── Endpoints ──────────────────────────────────────────────────────────────────


@app.get("/", summary="Health check")
async def root():
    return {"status": "ok", "message": "Mini-RAG API is running"}


@app.post("/ask", response_model=AskResponse, summary="Ask a question")
async def ask(payload: AskRequest):
    """
    Retrieve the most relevant context chunk and ask the LLM.
    """
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    context = rag.retrieve(payload.question)

    prompt = f"Контекст: {context}\n\nВопрос: {payload.question}"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set.")

    client = openai.AsyncOpenAI(api_key=api_key)
    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты полезный ассистент. Отвечай на русском языке."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=512,
        temperature=0.2,
    )

    answer = completion.choices[0].message.content.strip()
    return AskResponse(answer=answer, context=context)
