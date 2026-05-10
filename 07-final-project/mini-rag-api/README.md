# Mini-RAG API

A minimal **Retrieval-Augmented Generation** API built with **FastAPI**.  
Given a question it retrieves the most relevant text chunk from local `.txt` files
and sends a grounded prompt to the OpenAI API.

---

## System Requirements

| Resource | Minimum |
|----------|---------|
| RAM      | 16 GB   |
| GPU VRAM | 4 GB    |
| CPU      | 4 cores |
| Python   | 3.10+   |
| Docker   | 24.x+   |

---

## Project Structure

```
mini-rag-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & /ask endpoint
│   └── rag_engine.py    # Chunking, embedding, retrieval
├── docs/                # Knowledge base (.txt files)
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Quick Start

### 1. Clone & configure

```bash
git clone <your-repo-url>
cd mini-rag-api
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

The API will be available at **http://localhost:8000**  
Swagger UI: **http://localhost:8000/docs**

### 3. Run locally (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # set your key
uvicorn app.main:app --reload
```

---

## API Usage

### `POST /ask`

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

**Response:**

```json
{
  "answer": "RAG (Retrieval-Augmented Generation) is ...",
  "context": "Retrieval-Augmented Generation (RAG) is an AI architecture ..."
}
```

---

## Git Bash – Push to GitHub

```bash
# 1. Initialize repository
git init

# 2. Stage all files
git add .

# 3. First commit
git commit -m "feat: initial junior rag api"

# 4. Add remote and push
git remote add origin https://github.com/<your-username>/mini-rag-api.git
git branch -M main
git push -u origin main

# 5. Build & run with Docker
docker-compose up --build
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## How It Works

1. On startup, `RAGEngine` reads all `.txt` files from `docs/`.
2. Each file is split into **500-character chunks**.
3. All chunks are encoded with **`sentence-transformers/all-MiniLM-L6-v2`**.
4. On `POST /ask`, the question is encoded and the chunk with the highest
   **cosine similarity** is selected as context.
5. A prompt `"Контекст: {context}\n\nВопрос: {question}"` is sent to
   **OpenAI GPT-3.5-turbo**.
6. The answer and the retrieved context are returned in the response.

---

## License

MIT
