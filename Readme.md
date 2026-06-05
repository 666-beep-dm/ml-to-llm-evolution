# ML to LLM Evolution
### A Structured Engineering Progression from Classical Machine Learning to Production-Grade LLM Systems

---

## Problem Statement & Solution Overview

Modern AI engineering roles demand proficiency across the full ML spectrum — from tabular data modeling and feature engineering through to LLM prompting strategies, retrieval-augmented generation, fine-tuning, and containerized deployment. Most learning resources address these disciplines in isolation, leaving practitioners without a coherent mental model of how classical ML foundations translate into modern LLM system design. This repository bridges that gap by implementing each discipline as a standalone, reproducible module — progressing from Scikit-Learn pipelines through Transformer-based language model deployment — with consistent code quality and engineering practices applied at each stage. The result is a verifiable, end-to-end demonstration of applied AI engineering competency across two paradigm generations.

---

## Key Features

- **Progressive curriculum architecture**: Seven self-contained modules with explicit dependency ordering, enabling both sequential study and domain-specific deep dives.
- **Reproducible preprocessing pipelines**: Sklearn `Pipeline` + `ColumnTransformer` compositions covering imputation, encoding, and scaling with cross-validation-safe design.
- **Structured prompting implementations**: Zero-shot, few-shot, chain-of-thought, and role-prompting patterns with comparative evaluation harnesses.
- **Modular RAG engine**: Document ingestion, chunking strategies, vector store integration, and retrieval-augmented generation with configurable retriever/generator decoupling.
- **Containerized deployment**: Dockerized inference services with defined entrypoints, enabling environment-agnostic reproducibility.
- **Parameter-efficient fine-tuning**: LoRA/QLoRA configurations for adapting pretrained LLMs on domain-specific datasets without full-parameter retraining.
- **End-to-end final project**: Integrates components from all prior modules into a unified applied AI system demonstrating compositional system design.

---

## Architecture & Data Flow

The repository follows a **Layered Learning Architecture** — each module is a vertical slice that is independently runnable, but architecturally references the vocabulary and primitives established in prior modules. The overall system progression is:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ML TO LLM EVOLUTION                             │
├──────────────┬──────────────┬──────────────┬──────────────┬────────────┤
│  01-classic- │  02-llm-     │  03-         │  04-rag-     │ 05-deploy- │
│  ml          │  essentials  │  prompting   │  engine      │ ment       │
│              │              │              │              │            │
│ Tabular Data │ Tokenization │ Prompt       │ Doc Ingest   │ Dockerfile │
│ Preprocessing│ Embeddings   │ Templates    │ → Chunking   │ FastAPI /  │
│ Sklearn      │ Transformers │ Zero/Few/CoT │ → VectorDB   │ Inference  │
│ Pipelines    │ HuggingFace  │ Evaluation   │ → Retrieval  │ Endpoint   │
│ Evaluation   │ API Wrappers │              │ → Generation │            │
├──────────────┴──────────────┴──────────────┴──────────────┴────────────┤
│              06-fine-tuning              │    07-final-project          │
│                                          │                              │
│  Dataset Prep → LoRA Config → Training  │  Integrated Pipeline:        │
│  Loop → Checkpoint Management →         │  Classic ML + RAG + LLM +   │
│  Evaluation → Adapter Merge             │  Deployment + Fine-tuning    │
└──────────────────────────────────────────┴──────────────────────────────┘
```

**Data flow within a module (example: RAG engine):**

```
Raw Documents
     │
     ▼
[Loader / Parser]          ← PDF, TXT, HTML ingestion
     │
     ▼
[Text Chunker]             ← Recursive / semantic splitting with overlap
     │
     ▼
[Embedding Model]          ← Sentence Transformers / OpenAI Embeddings
     │
     ▼
[Vector Store]             ← FAISS / ChromaDB index
     │
  Query ──► [Retriever]    ← Top-k similarity search
                │
                ▼
         [LLM Generator]   ← Prompt assembly + API call
                │
                ▼
           [Response]
```

---

## Tech Stack

**Languages**
- Python 3.10+

**ML / Data Science**
- scikit-learn
- pandas
- numpy
- matplotlib / seaborn

**LLM & NLP**
- transformers (HuggingFace)
- sentence-transformers
- openai SDK
- tiktoken
- langchain / langchain-community

**Vector Databases**
- FAISS
- ChromaDB

**Fine-Tuning**
- peft (LoRA / QLoRA)
- trl
- bitsandbytes

**Serving / Infrastructure**
- FastAPI
- Docker
- uvicorn

**Notebooks & Experimentation**
- Jupyter Notebook / JupyterLab

---

## Project Structure

```
ml-to-llm-evolution/
│
├── 01-classic-ml/              # Tabular ML: preprocessing, feature engineering, model evaluation
│   ├── notebooks/              # EDA → pipeline construction → cross-validation
│   └── src/                    # Reusable preprocessing and evaluation utilities
│
├── 02-llm-essentials/          # LLM primitives: tokenization, embeddings, API interaction
│   ├── notebooks/              # HuggingFace model loading, embedding comparison
│   └── src/                    # LLM wrapper abstractions
│
├── 03-prompting/               # Prompt engineering patterns and evaluation
│   ├── notebooks/              # Zero-shot, few-shot, CoT, role-prompting experiments
│   └── templates/              # Parameterized prompt templates
│
├── 04-rag-engine/              # Retrieval-Augmented Generation pipeline
│   ├── notebooks/              # End-to-end RAG walkthrough
│   ├── src/
│   │   ├── ingestion.py        # Document loading and chunking
│   │   ├── embedder.py         # Embedding model interface
│   │   ├── retriever.py        # Vector store + top-k retrieval
│   │   └── generator.py        # LLM-based answer generation
│   └── data/                   # Sample knowledge base documents
│
├── 05-deployment/              # Containerized model serving
│   ├── app/                    # FastAPI inference application
│   ├── Dockerfile              # Multi-stage container build
│   └── docker-compose.yml      # Local service orchestration
│
├── 06-fine-tuning/             # Parameter-efficient LLM fine-tuning (LoRA/QLoRA)
│   ├── notebooks/              # Dataset prep, training loop, evaluation
│   ├── configs/                # LoRA hyperparameter configurations
│   └── src/                    # Training utilities, checkpoint management
│
└── 07-final-project/           # Integrated end-to-end AI system
    ├── pipeline/               # Orchestrates modules 01–06
    ├── api/                    # Unified inference API
    └── README.md               # Final project-specific documentation
```

---

## Installation & Quick Start

**Prerequisites:** Python 3.10+, Docker (for module 05)

```bash
# 1. Clone the repository
git clone https://github.com/666-beep-dm/ml-to-llm-evolution.git
cd ml-to-llm-evolution

# 2. Create and activate virtual environment
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (LLM API keys)
cp .env.example .env
# Edit .env with your OPENAI_API_KEY or HuggingFace token

# 5. Launch a module (example: RAG engine)
cd 04-rag-engine
jupyter notebook notebooks/rag_pipeline.ipynb

# 6. Run containerized deployment (module 05)
cd 05-deployment
docker build -t ml-llm-inference .
docker run -p 8000:8000 ml-llm-inference
```

---

## Usage Examples / Core API

### Classic ML Pipeline (Module 01)

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])
preprocessor = ColumnTransformer([
    ("num", numeric_pipeline, NUMERIC_COLS),
    ("cat", categorical_pipeline, CAT_COLS)
])
model = Pipeline([("prep", preprocessor), ("clf", GradientBoostingClassifier())])
model.fit(X_train, y_train)
```

### RAG Query (Module 04)

```python
from src.retriever import VectorRetriever
from src.generator import RAGGenerator

retriever = VectorRetriever(index_path="data/faiss_index")
generator = RAGGenerator(model="gpt-4o-mini")

query = "What are the key hyperparameters for LoRA fine-tuning?"
context_docs = retriever.retrieve(query, top_k=4)
answer = generator.generate(query=query, context=context_docs)
print(answer)
```

### Inference API (Module 05)

```bash
# Health check
curl http://localhost:8000/health

# Generate prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the key findings.", "use_rag": true}'

# Response
{
  "answer": "The key findings indicate...",
  "sources": ["doc_42", "doc_17"],
  "latency_ms": 312
}
```

### Fine-Tuning Launch (Module 06)

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer

lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"],
                          lora_dropout=0.05, bias="none", task_type="CAUSAL_LM")
model = get_peft_model(AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1"), lora_config)

trainer = SFTTrainer(model=model, train_dataset=dataset,
                     args=TrainingArguments(output_dir="./checkpoints", num_train_epochs=3,
                                           per_device_train_batch_size=4, gradient_accumulation_steps=4))
trainer.train()
```

---

## Skills Demonstrated

- **End-to-End ML Pipeline Design** — `ColumnTransformer` / `Pipeline` composition with cross-validation-safe preprocessing and feature engineering for tabular data.
- **Applied Transformer Architecture Understanding** — Tokenization mechanics, attention-based embedding extraction, and practical HuggingFace model loading and inference.
- **Prompt Engineering & Systematic Evaluation** — Structured implementation of zero-shot, few-shot, and chain-of-thought prompting with comparative quality assessment.
- **RAG System Architecture** — Document ingestion, chunking strategy selection, dense retrieval via vector store, and prompt-assembled generation with source attribution.
- **Containerized ML Serving** — Dockerfile authoring, FastAPI endpoint design, and reproducible container-based inference environment packaging.
- **Parameter-Efficient Fine-Tuning (PEFT)** — LoRA/QLoRA adapter configuration, supervised fine-tuning with `trl.SFTTrainer`, and checkpoint lifecycle management.
- **System Composition** — Integration of heterogeneous ML and LLM components into a unified inference pipeline with clear interface boundaries.
- **Reproducibility Engineering** — Environment isolation via `venv`, dependency pinning, `.env`-based secret management, and notebook-to-module code promotion patterns.

---

## Engineering Challenges & Solutions

**1. Chunking Strategy Tradeoffs in RAG Retrieval Quality**

Naive fixed-size chunking degrades retrieval precision when semantic units span chunk boundaries (e.g., multi-paragraph technical explanations). The RAG module addresses this by implementing recursive character-level splitting with configurable `chunk_size` / `chunk_overlap` parameters, preserving sentence and paragraph boundaries. Additionally, metadata propagation (source document, page number, section heading) is attached at ingest time, enabling post-retrieval filtering and source attribution without secondary lookups.

**2. Cross-Validation Leakage in Preprocessing Pipelines**

A common correctness failure in Scikit-Learn workflows is fitting scalers and encoders on the full training set before cross-validation folds are split, causing data leakage and optimistically biased validation metrics. Module 01 explicitly constructs `Pipeline` objects that defer all `fit` calls to within each CV fold's training split — eliminating leakage while keeping the preprocessing logic colocated with the model for clean deployment serialization via `joblib`.

**3. Memory Constraints in LLM Fine-Tuning**

Full-parameter fine-tuning of 7B+ parameter models exceeds consumer GPU VRAM budgets. Module 06 resolves this via QLoRA: 4-bit NF4 quantization (via `bitsandbytes`) reduces the frozen base model's footprint to ~4GB, while LoRA adapters inject trainable rank-16 matrices into attention projection layers only. Gradient checkpointing further reduces activation memory, making single-GPU fine-tuning viable. The adapter weights are merged post-training for clean inference without PEFT overhead.

---

## Key Takeaways & Growth

- **Cross-paradigm mental model**: Implementing both classical ML and LLM-based systems in one project surfaces the structural parallels — feature extraction maps to embedding, imputation pipelines map to prompt context construction, model evaluation maps to LLM output scoring — building transferable intuition between paradigms.
- **Production thinking at the module level**: Each module was designed with a deployment path in mind, not only notebook readability — enforcing separation between experimentation (notebooks) and reusable logic (src/) from the start.
- **Retrieval system design**: Building the RAG engine from scratch (rather than using a high-level abstraction) developed deep understanding of the embedding similarity–relevance gap, the impact of chunking granularity on recall, and the prompt construction patterns that minimize hallucination from retrieved context.
- **Constraint-driven optimization**: The fine-tuning module demonstrated that hardware constraints are an architectural input — LoRA rank, quantization precision, and batch accumulation settings must be jointly reasoned about, not treated as independent hyperparameters.

---

## Production Readiness & Future Improvements

| Area | Current State | Required for Production |
|------|--------------|------------------------|
| **Observability** | `print` / notebook output | Structured logging (loguru / OpenTelemetry), LLM call tracing, latency dashboards |
| **Evaluation Framework** | Manual notebook inspection | Automated RAG evaluation (RAGAS metrics: faithfulness, answer relevancy, context precision) |
| **API Hardening** | Basic FastAPI endpoint | Auth (API key / JWT), rate limiting, input validation with Pydantic v2, async concurrency |
| **CI/CD** | None | GitHub Actions: lint (ruff), type check (mypy), unit tests (pytest), Docker image build + push |
| **Vector Store Scalability** | FAISS / local ChromaDB | Managed vector DB (Pinecone / Weaviate) with persistent storage and index versioning |
| **Model Registry** | Local checkpoints | MLflow / HuggingFace Hub experiment tracking with artifact versioning |
| **Security** | `.env` secret management | Secrets manager (AWS SSM / HashiCorp Vault), no secrets in container layers |
| **Test Coverage** | Exploratory only | Unit tests for preprocessing transforms, retriever interface mocks, API endpoint contracts |

---

*Built by a practitioner navigating the transition from classical ML to modern LLM engineering — demonstrating that strong fundamentals and system design thinking are the constants across both paradigms.*