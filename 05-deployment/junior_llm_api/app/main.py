from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
import os

app = FastAPI(title="Junior LLM API", version="1.0.0")
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


@app.post("/ask", response_model=AnswerResponse)
async def ask(payload: QuestionRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": payload.question}],
        temperature=0.7,
        max_tokens=1024,
    )

    answer = completion.choices[0].message.content
    return AnswerResponse(answer=answer)
