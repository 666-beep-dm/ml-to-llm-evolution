"""src/utils/config_loader.py — Typed config loader from YAML."""

from __future__ import annotations
import logging
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    base_model_id:     str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    adapter_output_dir: str = "models/lora_adapter"
    merged_output_dir:  str = "models/merged"


@dataclass
class QuantConfig:
    load_in_4bit:              bool  = True
    bnb_4bit_quant_type:       str   = "nf4"
    bnb_4bit_compute_dtype:    str   = "float16"
    bnb_4bit_use_double_quant: bool  = True


@dataclass
class LoraConfig:
    r:              int        = 8
    lora_alpha:     int        = 16
    target_modules: List[str]  = field(default_factory=lambda: ["q_proj", "v_proj"])
    lora_dropout:   float      = 0.05
    bias:           str        = "none"
    task_type:      str        = "CAUSAL_LM"


@dataclass
class TrainingConfig:
    data_path:                    str   = "data/dataset.jsonl"
    train_split:                  float = 0.85
    seed:                         int   = 42
    per_device_train_batch_size:  int   = 1
    gradient_accumulation_steps:  int   = 8
    num_train_epochs:             int   = 3
    learning_rate:                float = 2e-4
    max_seq_length:               int   = 512
    warmup_ratio:                 float = 0.05
    logging_steps:                int   = 10
    save_steps:                   int   = 100
    save_total_limit:             int   = 2
    fp16:                         bool  = True
    gradient_checkpointing:       bool  = True
    optim:                        str   = "paged_adamw_32bit"
    lr_scheduler_type:            str   = "cosine"
    eval_strategy:                str   = "epoch"
    load_best_model_at_end:       bool  = True


@dataclass
class ApiConfig:
    host:               str   = "0.0.0.0"
    port:               int   = 8000
    max_new_tokens:     int   = 256
    temperature:        float = 0.7
    top_p:              float = 0.9
    repetition_penalty: float = 1.1


@dataclass
class PipelineConfig:
    model:    ModelConfig    = field(default_factory=ModelConfig)
    quant:    QuantConfig    = field(default_factory=QuantConfig)
    lora:     LoraConfig     = field(default_factory=LoraConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    api:      ApiConfig      = field(default_factory=ApiConfig)


def _merge(dataclass_instance, raw: dict) -> None:
    """Recursively overwrite dataclass fields from a dict."""
    for key, val in raw.items():
        if hasattr(dataclass_instance, key):
            setattr(dataclass_instance, key, val)


def load_config(path: str = "configs/training_config.yaml") -> PipelineConfig:
    cfg = PipelineConfig()
    p   = Path(path)
    if not p.exists():
        logger.warning("Config file not found at '%s', using defaults.", path)
        return cfg
    with p.open() as fh:
        raw = yaml.safe_load(fh) or {}
    _merge(cfg.model,    raw.get("model",        {}))
    _merge(cfg.quant,    raw.get("quantization",  {}))
    _merge(cfg.lora,     raw.get("lora",          {}))
    _merge(cfg.training, raw.get("training",      {}))
    _merge(cfg.api,      raw.get("api",           {}))
    logger.info("Config loaded from '%s'", path)
    return cfg
