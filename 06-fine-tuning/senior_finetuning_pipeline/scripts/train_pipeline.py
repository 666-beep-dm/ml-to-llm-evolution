"""scripts/train_pipeline.py — Training entry point."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import setup_logging
from src.utils.config_loader import load_config
from src.training.trainer import run_training

setup_logging()

if __name__ == "__main__":
    cfg = load_config()
    run_training(cfg)
