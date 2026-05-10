"""Centralised logging configuration."""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Set up root logger with a clean, structured format."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    logging.root.setLevel(level)
    logging.root.handlers = [handler]
