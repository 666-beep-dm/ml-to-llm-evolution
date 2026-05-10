"""
app/config.py  –  Centralised configuration for training and inference.
Modify this file to switch models or tune hyperparameters without touching
the training logic.
"""

from dataclasses import dataclass, field
from typing import List


# ── Model ─────────────────────────────────────────────────────────────────────
BASE_MODEL_ID: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# Alternative: "microsoft/Phi-3-mini-4k-instruct"

OUTPUT_ADAPTER_DIR: str = "output/lora_adapter"
MERGED_MODEL_DIR:   str = "output/merged_model"

# ── LoRA ──────────────────────────────────────────────────────────────────────
@dataclass
class LoraSettings:
    r:              int       = 8
    lora_alpha:     int       = 16
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    lora_dropout:   float     = 0.05
    bias:           str       = "none"
    task_type:      str       = "CAUSAL_LM"


# ── Training ──────────────────────────────────────────────────────────────────
@dataclass
class TrainSettings:
    data_path:                str   = "data/train.jsonl"
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8       # effective batch = 8
    num_train_epochs:         int   = 3
    learning_rate:            float = 2e-4
    max_seq_length:           int   = 512
    warmup_ratio:             float = 0.05
    logging_steps:            int   = 5
    save_steps:               int   = 50
    fp16:                     bool  = True
    gradient_checkpointing:   bool  = True     # key memory saver
    optim:                    str   = "paged_adamw_8bit"
    lr_scheduler_type:        str   = "cosine"
    report_to:                str   = "none"


# ── Quantization ──────────────────────────────────────────────────────────────
@dataclass
class QuantSettings:
    load_in_4bit:               bool  = True
    bnb_4bit_quant_type:        str   = "nf4"
    bnb_4bit_compute_dtype:     str   = "float16"
    bnb_4bit_use_double_quant:  bool  = True   # nested quantization


# Singletons used by other modules
LORA    = LoraSettings()
TRAIN   = TrainSettings()
QUANT   = QuantSettings()
