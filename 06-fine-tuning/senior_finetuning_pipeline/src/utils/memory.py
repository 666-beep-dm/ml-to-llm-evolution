"""src/utils/memory.py — GPU memory reporting utilities."""

from __future__ import annotations
import logging
import torch

logger = logging.getLogger(__name__)


def log_vram(label: str = "") -> None:
    if not torch.cuda.is_available():
        logger.info("[VRAM] CUDA unavailable%s", f" — {label}" if label else "")
        return
    allocated = torch.cuda.memory_allocated() / 1e9
    reserved  = torch.cuda.memory_reserved()  / 1e9
    total     = torch.cuda.get_device_properties(0).total_memory / 1e9
    logger.info(
        "[VRAM%s] allocated=%.2fGB  reserved=%.2fGB  total=%.2fGB",
        f" {label}" if label else "",
        allocated, reserved, total,
    )


def clear_cache() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.debug("CUDA cache cleared.")
