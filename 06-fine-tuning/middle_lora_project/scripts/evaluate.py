"""
scripts/evaluate.py  –  Side-by-side comparison of base vs LoRA-adapted model.

Usage:
    python scripts/evaluate.py
    python scripts/evaluate.py "What is LoRA?"
"""

import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
from app.config import OUTPUT_ADAPTER_DIR
from app.model_loader import load_base_model, load_with_adapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger("evaluate")

PROMPT_TEMPLATE = (
    "<|system|>\nYou are a helpful AI assistant.\n"
    "<|user|>\n{instruction}\n"
    "<|assistant|>\n"
)
MAX_NEW_TOKENS = 200


def generate(model, tokenizer, instruction: str) -> str:
    prompt = PROMPT_TEMPLATE.format(instruction=instruction)
    device = next(model.parameters()).device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_ids = output_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_ids, skip_special_tokens=True).strip()


def compare(instruction: str) -> None:
    sep = "─" * 60

    # ── Base model ────────────────────────────────────────────────
    logger.info("Loading BASE model …")
    tokenizer, base_model = load_base_model(quantize=True)
    base_model.eval()

    logger.info("Generating with BASE model …")
    base_answer = generate(base_model, tokenizer, instruction)

    # Free base model from GPU before loading adapter
    del base_model
    torch.cuda.empty_cache()

    # ── LoRA-adapted model ────────────────────────────────────────
    adapter_path = OUTPUT_ADAPTER_DIR
    if not os.path.exists(adapter_path):
        logger.error(
            "Adapter not found at '%s'. Run train.py first.", adapter_path
        )
        sys.exit(1)

    logger.info("Loading LORA model …")
    _, lora_model = load_with_adapter(adapter_path)

    logger.info("Generating with LORA model …")
    lora_answer = generate(lora_model, tokenizer, instruction)

    # ── Print comparison ──────────────────────────────────────────
    print(f"\n{sep}")
    print(f"  INSTRUCTION: {instruction}")
    print(sep)
    print("  BASE MODEL:")
    print(f"  {base_answer}")
    print(sep)
    print("  LORA-ADAPTED MODEL:")
    print(f"  {lora_answer}")
    print(f"{sep}\n")


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is LoRA?"
    compare(question)
