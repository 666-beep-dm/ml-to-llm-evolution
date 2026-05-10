"""
src/training/evaluator.py
Computes Perplexity on the test set and Cosine Similarity between
base-model and fine-tuned model outputs.
"""

from __future__ import annotations
import logging
import math
import torch
import torch.nn.functional as F
from typing import List, Tuple

from src.utils.config_loader import PipelineConfig
from src.utils.memory import log_vram, clear_cache
from src.training.data_module import build_datasets, CHAT_TEMPLATE
from src.training.model_factory import load_tokenizer, load_base_model, load_with_adapter

logger = logging.getLogger(__name__)


# ── Perplexity ────────────────────────────────────────────────────────────────

def compute_perplexity(model, tokenizer, texts: List[str], max_len: int = 512) -> float:
    model.eval()
    device     = next(model.parameters()).device
    total_loss = 0.0
    count      = 0

    with torch.no_grad():
        for text in texts:
            enc = tokenizer(text, return_tensors="pt",
                            truncation=True, max_length=max_len).to(device)
            labels = enc["input_ids"].clone()
            out    = model(**enc, labels=labels)
            total_loss += out.loss.item()
            count      += 1

    avg_loss = total_loss / max(count, 1)
    ppl      = math.exp(avg_loss)
    logger.info("Perplexity: %.4f  (avg loss: %.4f, n=%d)", ppl, avg_loss, count)
    return ppl


# ── Cosine Similarity ─────────────────────────────────────────────────────────

def _get_embedding(model, tokenizer, text: str, max_len: int = 256) -> torch.Tensor:
    device = next(model.parameters()).device
    enc    = tokenizer(text, return_tensors="pt",
                       truncation=True, max_length=max_len).to(device)
    with torch.no_grad():
        out = model(**enc, output_hidden_states=True)
    # Mean-pool last hidden state
    hidden = out.hidden_states[-1]           # (1, seq, hidden)
    emb    = hidden.mean(dim=1).squeeze(0)   # (hidden,)
    return emb.float()


def compute_cosine_similarities(
    base_model, lora_model, tokenizer,
    instructions: List[str],
) -> Tuple[float, List[float]]:
    scores = []
    for inst in instructions:
        prompt = CHAT_TEMPLATE.format(instruction=inst, response="")
        e_base = _get_embedding(base_model, tokenizer, prompt)
        e_lora = _get_embedding(lora_model, tokenizer, prompt)
        sim    = F.cosine_similarity(e_base.unsqueeze(0), e_lora.unsqueeze(0)).item()
        scores.append(sim)
        logger.debug("  cos_sim='%.4f'  inst='%s'", sim, inst[:60])
    avg = sum(scores) / len(scores) if scores else 0.0
    logger.info("Cosine Similarity: avg=%.4f  min=%.4f  max=%.4f",
                avg, min(scores, default=0), max(scores, default=0))
    return avg, scores


# ── Main evaluation routine ───────────────────────────────────────────────────

def run_evaluation(cfg: PipelineConfig) -> dict:
    import os
    adapter_dir = cfg.model.adapter_output_dir
    if not os.path.exists(adapter_dir):
        logger.error("Adapter not found at '%s'. Run training first.", adapter_dir)
        return {}

    _, test_ds = build_datasets(cfg.training.data_path, cfg.training.train_split, cfg.training.seed)
    if len(test_ds) == 0:
        logger.warning("Test split is empty — skipping evaluation.")
        return {}

    test_texts = test_ds["text"]
    instructions = test_ds["instruction"]

    # ── Base model ────────────────────────────────────────────────────────────
    logger.info("Loading BASE model for evaluation…")
    tokenizer  = load_tokenizer(cfg)
    base_model = load_base_model(cfg, quantize=True)
    base_model.eval()

    base_ppl = compute_perplexity(base_model, tokenizer, test_texts, cfg.training.max_seq_length)
    log_vram("base eval done")

    # keep base for cosine — clear after
    base_model_ref = base_model

    # ── LoRA model ────────────────────────────────────────────────────────────
    logger.info("Loading LORA model for evaluation…")
    _, lora_model = load_with_adapter(adapter_dir, cfg)
    lora_model.eval()

    lora_ppl = compute_perplexity(lora_model, tokenizer, test_texts, cfg.training.max_seq_length)
    log_vram("lora eval done")

    avg_cos, _ = compute_cosine_similarities(base_model_ref, lora_model, tokenizer, instructions)

    del base_model_ref, lora_model
    clear_cache()

    results = {
        "base_perplexity":  round(base_ppl, 4),
        "lora_perplexity":  round(lora_ppl, 4),
        "perplexity_delta": round(base_ppl - lora_ppl, 4),
        "avg_cosine_similarity": round(avg_cos, 4),
        "test_samples": len(test_texts),
    }
    logger.info("Evaluation results: %s", results)
    return results
