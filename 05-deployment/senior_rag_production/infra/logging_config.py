"""Structured JSON logging."""

import logging
import sys
from pythonjsonlogger.jsonlogger import JsonFormatter


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.root.setLevel(numeric)
    logging.root.handlers = [handler]
    for lib in ("httpx", "httpcore", "chromadb", "openai"):
        logging.getLogger(lib).setLevel(logging.WARNING)
