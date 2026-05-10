"""
Structured logging setup — writes to both stdout and logs/app.log.
"""

import logging
import sys
from pathlib import Path
from app.core.config import get_settings


def setup_logging() -> logging.Logger:
    settings = get_settings()

    log_path = Path(settings.log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path, encoding="utf-8"),
    ]

    logging.basicConfig(
        level=settings.log_level.upper(),
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
    )

    # Silence noisy third-party loggers
    for name in ("httpx", "httpcore", "chromadb", "sentence_transformers"):
        logging.getLogger(name).setLevel(logging.WARNING)

    return logging.getLogger("rag_service")


logger = setup_logging()
