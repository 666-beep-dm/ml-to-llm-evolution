# 🚀 Senior LoRA Fine-Tuning Pipeline

Production-ready pipeline for **LoRA fine-tuning** of a 1B LLM with
**4-bit quantization**, automated evaluation metrics, and a **FastAPI
inference API** — all containerised and GPU-ready.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Docker Compose                                         │
│                                                         │
│  ┌──────────────┐   weights/   ┌───────────────────┐   │
│  │   trainer    │  ──────────► │      api          │   │
│  │  (one-shot)  │   models/    │  POST /ask        │   │
│  └──────────────┘              │  GET  /health     │   │
│                                │  GET  /metrics    │   │
│  ┌──────────────┐              └───────────────────┘   │
│  │  evaluator   │  (optional profile)                  │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

## Hardware Requirements

| Component | Minimum |
|-----------|---------|
| CPU       | 4 cores (e.g. Intel Core i5-10300H) |
| RAM       | 16 GB |
| GPU VRAM  | 4 GB (NVIDIA, CUDA 11.8+) |
| Disk      | 15 GB free (model cache + checkpoints) |

---

## Project Structure

```
.
├── configs/
│   ├── training_config.yaml    # All hyperparameters
│   └── logging_config.yaml
├── src/
│   ├── training/
│   │   ├── data_module.py      # Load, validate, split dataset
│   │   ├── model_factory.py    # 4-bit load + LoRA wrapping
│   │   ├── trainer.py          # SFTTrainer orchestration
│   │   └── evaluator.py        # Perplexity + Cosine Similarity
│   ├── api/
│   │   ├── app.py              # FastAPI app + lifespan
│   │   ├── inference.py        # ModelRegistry + generate()
│   │   └── schemas.py          # Pydantic request/response models
│   └── utils/
│       ├── config_loader.py    # Typed YAML config loader
│       ├── logger.py           # Rotating file + console logging
│       └── memory.py           # VRAM monitoring helpers
├── scripts/
│   ├── train_pipeline.py       # Training entry point
│   ├── evaluate_pipeline.py    # Evaluation entry point
│   └── start_api.py            # Uvicorn launcher
├── data/
│   └── dataset.jsonl           # 50 instruction-response pairs
├── models/                     # Saved LoRA adapters
├── output/                     # eval_metrics.json + checkpoints
├── logs/                       # pipeline.log (rotating)
├── Dockerfile.trainer
├── Dockerfile.api
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Verify NVIDIA Container Toolkit

```bash
# Confirm GPU is accessible inside Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# If not installed:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
```

### 2. Git Bash — initialise repository

```bash
git init
git checkout -b main

# Stage all files
git add .
git commit -m "feat: lora fine-tuning pipeline — initial implementation"

# Create feature branch for experiments
git checkout -b feat/experiment-r16
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (API port, HF token for gated models)
```

### 4. Run training

```bash
# Build image and run the trainer (one-shot)
docker-compose up --build trainer
```

Logs are written to `logs/pipeline.log` and streamed to stdout.
Adapter weights are saved to `models/lora_adapter/`.

### 5. Run evaluation (optional)

```bash
docker-compose --profile evaluate up evaluator
# Metrics saved to output/eval_metrics.json
```

### 6. Start the inference API

```bash
docker-compose --profile api up api
```

API is available at **http://localhost:8000**
Interactive docs at **http://localhost:8000/docs**

---

## API Usage

### POST /ask

```bash
# Use fine-tuned model (default)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "What is LoRA?",
    "model_variant": "fine_tuned",
    "max_new_tokens": 200,
    "temperature": 0.7
  }'

# Compare with base model
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "What is LoRA?",
    "model_variant": "base_model"
  }'
```

### GET /metrics

```bash
curl http://localhost:8000/metrics
# Returns: base_perplexity, lora_perplexity, avg_cosine_similarity
```

### GET /health

```bash
curl http://localhost:8000/health
# Returns: status, cuda, base_loaded, lora_loaded
```

---

## VRAM Optimisation Stack

| Technique | Config value | Benefit |
|-----------|-------------|---------|
| NF4 double quantization | `bnb_4bit_use_double_quant=true` | ~75% weight compression |
| LoRA r=8, alpha=16 | `target_modules: [q_proj, v_proj]` | <0.1% trainable params |
| Gradient checkpointing | `gradient_checkpointing: true` | ~40% activation memory |
| Paged AdamW 32-bit | `optim: paged_adamw_32bit` | Optimizer states → CPU RAM |
| Batch 1 + accum 8 | Effective batch = 8 | No VRAM spikes |

Expected VRAM: **~3.2–3.8 GB** · Training time: **5–15 min** on 4 GB GPU.

---

## Switching Models

Edit `configs/training_config.yaml`:

```yaml
model:
  base_model_id: "microsoft/Phi-3-mini-4k-instruct"
```

No code changes required.

---

## Local Development (no Docker)

```bash
pip install -r requirements.txt

python scripts/train_pipeline.py
python scripts/evaluate_pipeline.py
python scripts/start_api.py
```
