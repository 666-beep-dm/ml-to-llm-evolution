"""
scripts/train.py  –  LoRA fine-tuning entry point.

Run from project root:
    python scripts/train.py
"""

import logging
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datasets import Dataset
from trl import SFTTrainer
from transformers import TrainingArguments

from app.config import TRAIN, OUTPUT_ADAPTER_DIR
from app.data_loader import build_text_list
from app.model_loader import load_base_model, apply_lora

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("output/train.log", mode="w"),
    ],
)
logger = logging.getLogger("train")


def main() -> None:
    logger.info("═" * 60)
    logger.info("Starting LoRA fine-tuning")
    logger.info("═" * 60)

    # 1. Load & prepare data
    texts   = build_text_list(TRAIN.data_path)
    dataset = Dataset.from_dict({"text": texts})
    logger.info("Dataset size: %d samples", len(dataset))

    # 2. Load model + apply LoRA
    tokenizer, base_model = load_base_model(quantize=True)
    model = apply_lora(base_model)

    if TRAIN.gradient_checkpointing:
        model.enable_input_require_grads()   # required with grad checkpointing + PEFT

    # 3. Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_ADAPTER_DIR,
        per_device_train_batch_size=TRAIN.per_device_train_batch_size,
        gradient_accumulation_steps=TRAIN.gradient_accumulation_steps,
        num_train_epochs=TRAIN.num_train_epochs,
        learning_rate=TRAIN.learning_rate,
        warmup_ratio=TRAIN.warmup_ratio,
        fp16=TRAIN.fp16,
        gradient_checkpointing=TRAIN.gradient_checkpointing,
        logging_steps=TRAIN.logging_steps,
        save_steps=TRAIN.save_steps,
        optim=TRAIN.optim,
        lr_scheduler_type=TRAIN.lr_scheduler_type,
        report_to=TRAIN.report_to,
        save_total_limit=2,
    )

    # 4. SFTTrainer (handles tokenisation internally)
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=TRAIN.max_seq_length,
        args=training_args,
    )

    # 5. Train
    logger.info("Training started …")
    trainer.train()
    logger.info("Training complete.")

    # 6. Save adapter
    os.makedirs(OUTPUT_ADAPTER_DIR, exist_ok=True)
    trainer.model.save_pretrained(OUTPUT_ADAPTER_DIR)
    tokenizer.save_pretrained(OUTPUT_ADAPTER_DIR)
    logger.info("Adapter saved to '%s'", OUTPUT_ADAPTER_DIR)


if __name__ == "__main__":
    main()
