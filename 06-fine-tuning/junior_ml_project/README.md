# 🤖 Junior ML Micro Fine-Tune Project

Fine-tune **distilgpt2** on a tiny local QA dataset — designed for low-VRAM GPUs.

---

## Hardware Requirements

| Component | Minimum Spec |
|-----------|-------------|
| CPU       | 4 cores (e.g. Intel Core i5-10300H) |
| RAM       | 16 GB |
| GPU VRAM  | 4 GB (e.g. NVIDIA GTX 1650 Ti) |
| Disk      | 5 GB free |

---

## Project Structure

```
.
├── data/
│   └── qa_dataset.json       # 10 QA training pairs
├── scripts/
│   ├── train.py              # Fine-tuning script
│   └── predict.py            # Inference script
├── models/
│   └── finetuned/            # Saved weights (after training)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Quick Start (Docker — recommended)

### 1. Install NVIDIA Container Toolkit

Follow the official guide:
👉 https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

### 2. Git Bash commands

```bash
# Initialise repo
git init
git add .
git commit -m "feat: initial mini-tuning project"

# Build image and run training
docker-compose up --build
```

### 3. Run inference (after training)

```bash
docker-compose --profile predict up predict
```

---

## Local (no Docker)

```bash
pip install -r requirements.txt

# Train
python scripts/train.py

# Predict
python scripts/predict.py "What is a neural network?"
```

---

## Key Optimisations for 4 GB VRAM

| Technique | Value | Effect |
|-----------|-------|--------|
| `batch_size` | 1 | Minimal VRAM per step |
| `gradient_accumulation_steps` | 8 | Effective batch of 8 |
| `mixed_precision` (fp16) | enabled via `accelerate` | ~2× VRAM saving |
| Model | distilgpt2 (82 M params) | Fits comfortably in 4 GB |

Expected training time: **3–7 minutes** on GTX 1650 Ti.

---

## Expected Output

```
[INFO] Device: cuda
[INFO] Loading model 'distilgpt2' ...
Epoch 1/3  |  avg loss: 3.2145
Epoch 2/3  |  avg loss: 2.0871
Epoch 3/3  |  avg loss: 1.4302
[INFO] Model saved to 'models/finetuned'
```
