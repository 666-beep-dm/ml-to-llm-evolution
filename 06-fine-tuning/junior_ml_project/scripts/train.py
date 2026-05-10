"""
train.py  –  Micro fine-tune distilgpt2 on local QA dataset.
Optimised for 4 GB VRAM: batch_size=1, gradient_accumulation, fp16.
"""

import json
import os
from pathlib import Path

import torch
from accelerate import Accelerator
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, AdamW

# ── Config ──────────────────────────────────────────────────────────────────
MODEL_NAME              = "distilgpt2"
DATA_PATH               = "data/qa_dataset.json"
OUTPUT_DIR              = "models/finetuned"
EPOCHS                  = 3
BATCH_SIZE              = 1
GRADIENT_ACCUM_STEPS    = 8   # effective batch = 8
LR                      = 5e-5
MAX_LEN                 = 128
# ────────────────────────────────────────────────────────────────────────────


class QADataset(Dataset):
    """Simple dataset that formats QA pairs as 'Q: ... A: ...' prompts."""

    def __init__(self, path: str, tokenizer, max_len: int):
        with open(path) as f:
            pairs = json.load(f)

        self.encodings = []
        for item in pairs:
            text = f"Q: {item['question']}\nA: {item['answer']}<|endoftext|>"
            enc = tokenizer(
                text,
                truncation=True,
                max_length=max_len,
                padding="max_length",
                return_tensors="pt",
            )
            input_ids = enc["input_ids"].squeeze()
            # labels = input_ids (causal LM, shift handled inside model)
            self.encodings.append({"input_ids": input_ids, "labels": input_ids.clone()})

    def __len__(self):
        return len(self.encodings)

    def __getitem__(self, idx):
        return self.encodings[idx]


def main():
    accelerator = Accelerator(mixed_precision="fp16")

    print(f"[INFO] Device: {accelerator.device}")
    print(f"[INFO] Loading model '{MODEL_NAME}' ...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    dataset = QADataset(DATA_PATH, tokenizer, MAX_LEN)
    loader  = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    optimizer = AdamW(model.parameters(), lr=LR)

    model, optimizer, loader = accelerator.prepare(model, optimizer, loader)

    model.train()
    for epoch in range(1, EPOCHS + 1):
        total_loss = 0.0
        optimizer.zero_grad()

        for step, batch in enumerate(loader, start=1):
            outputs = model(**batch)
            loss    = outputs.loss / GRADIENT_ACCUM_STEPS
            accelerator.backward(loss)
            total_loss += outputs.loss.item()

            if step % GRADIENT_ACCUM_STEPS == 0:
                optimizer.step()
                optimizer.zero_grad()

        avg = total_loss / len(loader)
        print(f"Epoch {epoch}/{EPOCHS}  |  avg loss: {avg:.4f}")

    # Save
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    unwrapped = accelerator.unwrap_model(model)
    unwrapped.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"[INFO] Model saved to '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()
