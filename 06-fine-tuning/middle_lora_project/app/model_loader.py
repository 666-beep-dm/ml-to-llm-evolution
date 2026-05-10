"""
app/model_loader.py  –  Load the base model with BnB 4-bit quantization
and wrap it with LoRA adapters via PEFT.
"""

import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel

from app.config import BASE_MODEL_ID, LORA, QUANT

logger = logging.getLogger(__name__)


def get_bnb_config() -> BitsAndBytesConfig:
    compute_dtype = getattr(torch, QUANT.bnb_4bit_compute_dtype)
    return BitsAndBytesConfig(
        load_in_4bit=QUANT.load_in_4bit,
        bnb_4bit_quant_type=QUANT.bnb_4bit_quant_type,
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=QUANT.bnb_4bit_use_double_quant,
    )


def load_base_model(quantize: bool = True):
    """Load tokenizer + causal LM, optionally 4-bit quantized."""
    logger.info("Loading tokenizer for '%s' ...", BASE_MODEL_ID)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token    = tokenizer.eos_token
    tokenizer.padding_side = "right"

    bnb_cfg = get_bnb_config() if quantize else None
    logger.info("Loading model (4-bit=%s) ...", quantize)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        quantization_config=bnb_cfg,
        device_map="auto",
        trust_remote_code=True,
    )
    _log_memory("after base model load")
    return tokenizer, model


def apply_lora(model):
    """Prepare model for k-bit training and wrap with LoRA adapters."""
    model = prepare_model_for_kbit_training(model)

    lora_cfg = LoraConfig(
        r=LORA.r,
        lora_alpha=LORA.lora_alpha,
        target_modules=LORA.target_modules,
        lora_dropout=LORA.lora_dropout,
        bias=LORA.bias,
        task_type=LORA.task_type,
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()
    _log_memory("after LoRA wrapping")
    return model


def load_with_adapter(adapter_dir: str):
    """Load base model and attach a saved LoRA adapter for inference."""
    logger.info("Loading base + adapter from '%s' ...", adapter_dir)
    tokenizer, base = load_base_model(quantize=True)
    model = PeftModel.from_pretrained(base, adapter_dir)
    model.eval()
    return tokenizer, model


def _log_memory(label: str) -> None:
    if torch.cuda.is_available():
        used  = torch.cuda.memory_allocated() / 1e9
        total = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info("[VRAM %s] %.2f / %.2f GB", label, used, total)
    else:
        logger.info("[VRAM %s] CUDA not available", label)
