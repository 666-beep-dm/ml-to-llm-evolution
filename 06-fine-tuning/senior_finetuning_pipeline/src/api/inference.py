"""src/api/inference.py — Model registry with lazy loading."""

from __future__ import annotations
import logging
import os
import torch
from typing import Optional

from src.utils.config_loader import PipelineConfig
from src.utils.memory import log_vram, clear_cache
from src.training.model_factory import load_tokenizer, load_base_model, load_with_adapter

logger = logging.getLogger(__name__)

PROMPT_TMPL = (
    "<|system|>\nYou are a helpful AI assistant.\n"
    "<|user|>\n{instruction}\n"
    "<|assistant|>\n"
)


class ModelRegistry:
    """Holds base and LoRA models with lazy initialisation."""

    def __init__(self, cfg: PipelineConfig) -> None:
        self.cfg         = cfg
        self._tokenizer  = None
        self._base_model = None
        self._lora_model = None

    # ── Lazy loaders ─────────────────────────────────────────────────────────

    def _ensure_tokenizer(self):
        if self._tokenizer is None:
            self._tokenizer = load_tokenizer(self.cfg)

    def get_base(self):
        self._ensure_tokenizer()
        if self._base_model is None:
            logger.info("Lazy-loading BASE model…")
            self._base_model = load_base_model(self.cfg, quantize=True)
            self._base_model.eval()
            log_vram("base model ready")
        return self._tokenizer, self._base_model

    def get_lora(self):
        self._ensure_tokenizer()
        if self._lora_model is None:
            adapter = self.cfg.model.adapter_output_dir
            if not os.path.exists(adapter):
                raise FileNotFoundError(
                    f"Adapter not found at '{adapter}'. Run training first."
                )
            logger.info("Lazy-loading LORA model…")
            _, self._lora_model = load_with_adapter(adapter, self.cfg)
            log_vram("lora model ready")
        return self._tokenizer, self._lora_model

    @property
    def base_loaded(self) -> bool:
        return self._base_model is not None

    @property
    def lora_loaded(self) -> bool:
        return self._lora_model is not None


def generate(
    model,
    tokenizer,
    instruction: str,
    max_new_tokens: int = 256,
    temperature:    float = 0.7,
    top_p:          float = 0.9,
    repetition_penalty: float = 1.1,
) -> str:
    prompt = PROMPT_TMPL.format(instruction=instruction)
    device = next(model.parameters()).device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        out_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_ids = out_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_ids, skip_special_tokens=True).strip()
