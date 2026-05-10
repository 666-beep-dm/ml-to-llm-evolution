"""src/training/model_factory.py — Model / tokenizer factory with LoRA setup."""

from __future__ import annotations
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import (LoraConfig, get_peft_model,
                  prepare_model_for_kbit_training, PeftModel)

from src.utils.config_loader import PipelineConfig
from src.utils.memory import log_vram

logger = logging.getLogger(__name__)


def build_bnb_config(cfg: PipelineConfig) -> BitsAndBytesConfig:
    compute_dtype = getattr(torch, cfg.quant.bnb_4bit_compute_dtype)
    return BitsAndBytesConfig(
        load_in_4bit=cfg.quant.load_in_4bit,
        bnb_4bit_quant_type=cfg.quant.bnb_4bit_quant_type,
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=cfg.quant.bnb_4bit_use_double_quant,
    )


def load_tokenizer(cfg: PipelineConfig):
    tok = AutoTokenizer.from_pretrained(
        cfg.model.base_model_id, trust_remote_code=True
    )
    tok.pad_token    = tok.eos_token
    tok.padding_side = "right"
    logger.info("Tokenizer loaded: vocab_size=%d", tok.vocab_size)
    return tok


def load_base_model(cfg: PipelineConfig, quantize: bool = True):
    logger.info("Loading base model '%s' (4-bit=%s)…", cfg.model.base_model_id, quantize)
    bnb = build_bnb_config(cfg) if quantize else None
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model.base_model_id,
        quantization_config=bnb,
        device_map="auto",
        trust_remote_code=True,
    )
    log_vram("base model loaded")
    return model


def apply_lora(model, cfg: PipelineConfig):
    model = prepare_model_for_kbit_training(model)
    lora_cfg = LoraConfig(
        r=cfg.lora.r,
        lora_alpha=cfg.lora.lora_alpha,
        target_modules=cfg.lora.target_modules,
        lora_dropout=cfg.lora.lora_dropout,
        bias=cfg.lora.bias,
        task_type=cfg.lora.task_type,
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()
    log_vram("LoRA applied")
    return model


def load_with_adapter(adapter_dir: str, cfg: PipelineConfig):
    """Load quantized base + saved LoRA adapter (for inference)."""
    logger.info("Loading adapter from '%s'…", adapter_dir)
    tok   = load_tokenizer(cfg)
    base  = load_base_model(cfg, quantize=True)
    model = PeftModel.from_pretrained(base, adapter_dir)
    model.eval()
    log_vram("adapter loaded")
    return tok, model
