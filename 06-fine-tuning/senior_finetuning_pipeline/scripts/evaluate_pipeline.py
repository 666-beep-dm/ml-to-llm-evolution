"""scripts/evaluate_pipeline.py — Evaluation entry point."""

import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import setup_logging
from src.utils.config_loader import load_config
from src.training.evaluator import run_evaluation

setup_logging()

if __name__ == "__main__":
    cfg     = load_config()
    results = run_evaluation(cfg)
    os.makedirs("output", exist_ok=True)
    out = "output/eval_metrics.json"
    with open(out, "w") as fh:
        json.dump(results, fh, indent=2)
    print(json.dumps(results, indent=2))
    print(f"Metrics saved → {out}")
