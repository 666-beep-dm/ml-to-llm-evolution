# Semantic Search Engine

Отказоустойчивый микросервис семантического поиска на FastAPI + FAISS + sentence-transformers.

## Структура

```
src/
├── api/          # HTTP-слой (роуты, DI)
├── core/         # Бизнес-логика (embedder, search service)
├── db/           # Хранилище (абстракция + FAISS)
└── schemas/      # Pydantic-модели
tests/            # Интеграционные тесты
```

## Запуск локально

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
# → http://localhost:8000/docs
```

## Docker

```bash
docker build -t semantic-search .
docker run -p 8000:8000 semantic-search
```

## Тесты

```bash
pytest tests/ -v
```

## API

| Метод  | Путь                  | Описание                      |
|--------|-----------------------|-------------------------------|
| POST   | /api/v1/documents     | Добавить документы батчем     |
| GET    | /api/v1/search        | Семантический поиск           |
| DELETE | /api/v1/documents     | Очистить индекс               |
| GET    | /health               | Статус сервиса                |

## Ключевые решения

| Решение | Обоснование |
|---------|-------------|
| Repository Pattern | Смена FAISS на Qdrant без изменения бизнес-логики |
| lru_cache на модели | Одна загрузка за жизнь процесса |
| LRU-кэш эмбеддингов | Дубли текстов не пересчитываются |
| Батч-кодирование | Один вызов model.encode() для N текстов |
| Background Task | Индексация не блокирует HTTP-ответ |
| run_in_executor | ML-вычисления не блокируют event loop |
| IndexFlatIP + нормализация | Точный косинусный поиск без аппроксимации |