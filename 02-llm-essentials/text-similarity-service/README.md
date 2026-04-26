# Text Similarity Microservice

FastAPI-микросервис для семантического анализа текстов на базе `sentence-transformers`.

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Документация: http://localhost:8000/docs

## Запуск через Docker

```bash
docker build -t text-similarity .
docker run -p 8000:8000 text-similarity
```

## Пример запроса

```bash
curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{
           "texts": [
             "A cat is sitting on a warm windowsill.",
             "A fluffy kitten rests on a sunny ledge.",
             "Python programming is a lot of fun.",
             "I enjoy coding in Python every day."
           ]
         }'
```

## Пример ответа

```json
{
  "total_texts": 4,
  "top_pairs": [
    {
      "index_a": 0, "index_b": 1,
      "text_a": "A cat is sitting on a warm windowsill.",
      "text_b": "A fluffy kitten rests on a sunny ledge.",
      "score": 0.812453
    },
    {
      "index_a": 2, "index_b": 3,
      "text_a": "Python programming is a lot of fun.",
      "text_b": "I enjoy coding in Python every day.",
      "score": 0.734211
    },
    {
      "index_a": 1, "index_b": 2,
      "text_a": "A fluffy kitten rests on a sunny ledge.",
      "text_b": "Python programming is a lot of fun.",
      "score": 0.102341
    }
  ]
}
```

## Обработка ошибок

| Статус | Причина |
|--------|---------|
| 422    | Менее 2 текстов, пустые строки, превышение длины |
| 500    | Внутренняя ошибка ML-обработки |
