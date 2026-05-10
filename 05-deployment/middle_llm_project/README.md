# Middle LLM API

A **production-ready**, modular FastAPI service for conversational AI with:
- ✅ Conversation history support
- ✅ Robust error handling (timeouts, rate limits, empty responses)
- ✅ `pydantic-settings` configuration
- ✅ Multi-stage Docker build
- ✅ Structured logging

---

## Project Structure

```
middle_llm_project/
├── app/
│   ├── api/
│   │   └── router.py        # Thin controller — only HTTP concerns
│   ├── core/
│   │   ├── config.py        # pydantic-settings (reads .env)
│   │   └── logging_config.py
│   ├── schemas/
│   │   └── chat.py          # Request / Response models (Pydantic v2)
│   ├── services/
│   │   ├── llm_service.py   # All OpenAI logic
│   │   └── exceptions.py    # Domain exceptions
│   └── main.py              # App factory + lifespan
├── tests/
│   └── test_ask_endpoint.py
├── .env                     # ⚠ Never commit this
├── .gitignore
├── docker-compose.yml
├── Dockerfile               # Multi-stage build
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Quick Start

### Option A — Docker (recommended)

```bash
# 1. Set your API key
echo "OPENAI_API_KEY=sk-..." >> .env

# 2. Build and start
docker-compose up --build

# 3. Stop
docker-compose down
```

### Option B — Local (Git Bash / macOS / Linux)

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
# source venv/bin/activate         # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Set your API key
cp .env .env   # already exists — just fill in OPENAI_API_KEY

# 4. Run the server
uvicorn app.main:app --reload
```

Server: **http://localhost:8000**
Interactive docs: **http://localhost:8000/docs**

---

## API Reference

### `POST /api/v1/ask`

```json
{
  "question": "And what about Germany?",
  "history": [
    {"role": "user",      "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."}
  ],
  "system_prompt": "Answer only in German."
}
```

**Response `200`**

```json
{
  "answer": "Die Hauptstadt Deutschlands ist Berlin.",
  "model": "gpt-4o-mini",
  "prompt_tokens": 42,
  "completion_tokens": 9
}
```

**Error responses**

| Status | Meaning                        |
|--------|--------------------------------|
| 422    | Validation error (bad payload) |
| 429    | Rate limit hit                 |
| 502    | Empty / unexpected LLM reply   |
| 504    | LLM request timed out          |
| 500    | Unhandled internal error       |

### `GET /health`

```json
{"status": "ok", "model": "gpt-4o-mini"}
```

---

## Running Tests

```bash
pytest -v
```

---

## Configuration (`.env`)

| Variable        | Default       | Description                  |
|-----------------|---------------|------------------------------|
| OPENAI_API_KEY  | *(required)*  | Your OpenAI secret key       |
| MODEL_NAME      | gpt-4o-mini   | Model identifier             |
| TEMPERATURE     | 0.7           | Sampling temperature 0–2     |
| MAX_TOKENS      | 1024          | Max tokens in response       |
| TIMEOUT         | 30.0          | Request timeout in seconds   |

---

## Git Bash — First Push to GitHub

```bash
# Inside the project folder:
git init
git add .
git commit -m "feat: middle-level FastAPI LLM API with history and error handling"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/middle_llm_project.git
git push -u origin main
```

> ⚠️ **Always verify** `.env` is NOT staged before committing:
> ```bash
> git status   # .env must NOT appear in the list
> ```
