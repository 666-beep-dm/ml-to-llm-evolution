"""scripts/start_api.py — Launch FastAPI server."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uvicorn
from src.utils.config_loader import load_config

if __name__ == "__main__":
    cfg = load_config()
    uvicorn.run(
        "src.api.app:app",
        host=cfg.api.host,
        port=cfg.api.port,
        reload=False,
        log_level="info",
    )
