from pydantic import BaseModel, Field, field_validator


class DocumentItem(BaseModel):
    doc_id: str = Field(..., description="Уникальный идентификатор документа")
    text: str = Field(..., description="Текст документа")

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Текст документа не может быть пустым.")
        if len(v) > 50_000:
            raise ValueError("Текст превышает допустимую длину в 50 000 символов.")
        return v

    @field_validator("doc_id")
    @classmethod
    def doc_id_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("doc_id не может быть пустым.")
        return v


class AddDocumentsRequest(BaseModel):
    documents: list[DocumentItem] = Field(..., min_length=1)


class SearchRequest(BaseModel):
    query: str = Field(..., description="Поисковый запрос")
    top_k: int = Field(default=5, ge=1, le=100, description="Количество результатов")

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Поисковый запрос не может быть пустым.")
        return v


class AddDocumentsResponse(BaseModel):
    added: int
    total_indexed: int
    skipped_duplicates: int = 0


class SearchResult(BaseModel):
    doc_id: str
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total_indexed: int


class DeleteResponse(BaseModel):
    deleted: int
    message: str
