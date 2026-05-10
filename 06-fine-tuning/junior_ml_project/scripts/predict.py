"""
predict.py  –  Run inference with the fine-tuned model.

Usage:
    python scripts/predict.py "What is overfitting?"
"""

import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_DIR = "models/finetuned"
MAX_NEW_TOKENS = 80


def generate(question: str) -> str:
    model_path = Path(MODEL_DIR)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Fine-tuned model not found at '{MODEL_DIR}'. "
            "Run train.py first."
        )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    tokenizer.pad_token = tokenizer.eos_token

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model  = AutoModelForCausalLM.from_pretrained(MODEL_DIR).to(device)
    model.eval()

    prompt = f"Q: {question}\nA:"
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only the newly generated tokens
    new_ids = output_ids[0][inputs["input_ids"].shape[1]:]
    answer  = tokenizer.decode(new_ids, skip_special_tokens=True).strip()
    return answer


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is machine learning?"
    print(f"Question : {question}")
    print(f"Answer   : {generate(question)}")
