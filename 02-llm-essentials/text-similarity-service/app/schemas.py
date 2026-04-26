from pydantic import BaseModel, field_validator
from typing import List


class AnalyzeRequest(BaseModel):
    texts: List[str]

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, texts: List[str]) -> List[str]:
        if len(texts) < 2:
            raise ValueError("Необходимо передать минимум 2 текста.")

        cleaned = []
        for i, text in enumerate(texts):
            stripped = text.strip()
            if not stripped:
                raise ValueError(
                    f"Текст с индексом {i} пустой или содержит только пробелы."
                )
            if len(stripped) > 10_000:
                raise ValueError(
                    f"Текст с индексом {i} превышает допустимую длину в 10 000 символов."
                )
            cleaned.append(stripped)

        return cleaned


class SimilarPair(BaseModel):
    index_a: int
    index_b: int
    text_a: str
    text_b: str
    score: float


class AnalyzeResponse(BaseModel):
    total_texts: int
    top_pairs: List[SimilarPair]
