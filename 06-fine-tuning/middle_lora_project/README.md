# 🧠 Middle LoRA Fine-Tuning Project

Parameter-Efficient Fine-Tuning of **TinyLlama-1.1B** using **LoRA + 4-bit quantization**.  
Designed for consumer GPUs with **4 GB VRAM**.

---

## Hardware Requirements

| Component | Minimum Spec |
|-----------|-------------|
| CPU       | 4 cores (e.g. Intel Core i5-10300H) |
| RAM       | 16 GB |
| GPU VRAM  | 4 GB (NVIDIA, CUDA 12.1+) |
| Disk      | 10 GB free (model cache) |

---

## Project Structure

```
.
├── app/
│   ├── config.py          # All hyperparameters in one place
│   ├── data_loader.py     # JSONL loading + prompt formatting
│   └── model_loader.py    # 4-bit model load + LoRA wrapping
├── data/
│   └── train.jsonl        # 30 instruction-response pairs
├── output/                # Saved LoRA adapters + training log
├── scripts/
│   ├── train.py           # Fine-tuning entry point
│   └── evaluate.py        # Base vs LoRA comparison
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Quick Start (Docker)

### 1. Verify NVIDIA Container Toolkit

```bash
# Check that the toolkit is installed and working
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# If not installed, follow the official guide:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
```

### 2. Git Bash — initialise repository

```bash
git init
git add .
git commit -m "feat: lora fine-tuning implementation"
```

### 3. Build image and run training

```bash
docker-compose up --build
```

Training logs are written to `output/train.log`.

### 4. Compare base vs fine-tuned model

```bash
docker-compose --profile evaluate up evaluate
```

---

## Local Setup (no Docker)

```bash
pip install -r requirements.txt

# Train
python scripts/train.py

# Evaluate
python scripts/evaluate.py "What is LoRA?"
```

---

## Key Optimisations for 4 GB VRAM

| Technique | Setting | Effect |
|-----------|---------|--------|
| 4-bit NF4 quantization | `bnb_4bit_quant_type=nf4` | 4× weight compression |
| Double quantization | `use_double_quant=True` | Additional ~0.4 bpp saving |
| LoRA rank | `r=8` | Only 0.1% of params trainable |
| Gradient checkpointing | `True` | Trades compute for memory |
| Batch size | `1` + `accum=8` | Effective batch of 8 |
| Paged AdamW 8-bit | `paged_adamw_8bit` | Optimizer states in CPU RAM |

Expected VRAM usage: **~3.2–3.8 GB**.  
Expected training time: **5–15 minutes** on a 4 GB GPU.

---

## Configuration

All training parameters live in `app/config.py`. Key knobs:

```python
# Switch model
BASE_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

# Adjust LoRA rank
LORA.r = 16           # more capacity, more memory
LORA.lora_alpha = 32  # keep alpha = 2 × r as a rule of thumb

# Speed up training
TRAIN.num_train_epochs = 1
```
