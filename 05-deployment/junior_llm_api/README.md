# Junior LLM API

Минималистичный FastAPI-сервис для общения с LLM через OpenAI API.

## Эндпоинты

| Метод | Путь   | Описание               |
|-------|--------|------------------------|
| POST  | `/ask` | Задать вопрос модели   |

**Пример запроса:**
```json
{
  "question": "Что такое FastAPI?"
}
```

**Пример ответа:**
```json
{
  "answer": "FastAPI — это современный веб-фреймворк для Python..."
}
```

## Запуск через Docker

### 1. Настройте API-ключ

Откройте файл `.env` и вставьте ваш OpenAI API-ключ:

```
OPENAI_API_KEY=sk-...
```

### 2. Соберите и запустите контейнер

```bash
docker-compose up --build
```

Сервис будет доступен по адресу: **http://localhost:8000**

Интерактивная документация: **http://localhost:8000/docs**

### 3. Остановка

```bash
docker-compose down
```

## Локальный запуск (без Docker)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env .env                    # убедитесь, что ключ указан
uvicorn app.main:app --reload
```

## Структура проекта

```
junior_llm_api/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI-приложение
├── .env                 # Секреты (не коммитить!)
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```
