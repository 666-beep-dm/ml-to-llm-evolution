"""src/training/trainer.py — Training orchestration."""

from __future__ import annotations
import logging
import os
from pathlib import Path

from transformers import TrainingArguments
from trl import SFTTrainer

from src.utils.config_loader import PipelineConfig
from src.utils.memory import log_vram
from src.training.data_module import build_datasets
from src.training.model_factory import load_tokenizer, load_base_model, apply_lora

logger = logging.getLogger(__name__)


def run_training(cfg: PipelineConfig) -> None:
    logger.info("═" * 64)
    logger.info("  LoRA Fine-Tuning Pipeline — START")
    logger.info("═" * 64)

    # 1. Data
    train_ds, _ = build_datasets(cfg.training.data_path, cfg.training.train_split, cfg.training.seed)
    logger.info("Training samples: %d", len(train_ds))

    # 2. Model
    tokenizer = load_tokenizer(cfg)
    model     = load_base_model(cfg, quantize=True)
    model     = apply_lora(model, cfg)

    if cfg.training.gradient_checkpointing:
        model.enable_input_require_grads()

    # 3. Training args
    Path(cfg.model.adapter_output_dir).mkdir(parents=True, exist_ok=True)
    args = TrainingArguments(
        output_dir=cfg.model.adapter_output_dir,
        per_device_train_batch_size=cfg.training.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.training.gradient_accumulation_steps,
        num_train_epochs=cfg.training.num_train_epochs,
        learning_rate=cfg.training.learning_rate,
        warmup_ratio=cfg.training.warmup_ratio,
        fp16=cfg.training.fp16,
        gradient_checkpointing=cfg.training.gradient_checkpointing,
        logging_steps=cfg.training.logging_steps,
        save_steps=cfg.training.save_steps,
        save_total_limit=cfg.training.save_total_limit,
        optim=cfg.training.optim,
        lr_scheduler_type=cfg.training.lr_scheduler_type,
        eval_strategy=cfg.training.eval_strategy,
        load_best_model_at_end=cfg.training.load_best_model_at_end,
        report_to="none",
    )

    # 4. SFTTrainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        dataset_text_field="text",
        max_seq_length=cfg.training.max_seq_length,
        args=args,
    )

    # 5. Train
    logger.info("Starting training…")
    trainer.train()
    log_vram("post-training")

    # 6. Save adapter
    trainer.model.save_pretrained(cfg.model.adapter_output_dir)
    tokenizer.save_pretrained(cfg.model.adapter_output_dir)
    logger.info("Adapter saved → '%s'", cfg.model.adapter_output_dir)
    logger.info("═" * 64)
    logger.info("  Training complete.")
    logger.info("═" * 64)
