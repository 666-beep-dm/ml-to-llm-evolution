"""
Structured logging setup using loguru.
Import `logger` from here across the entire project.
"""

import sys
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """Configure loguru with a structured format."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        level=settings.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )
    # Also log to file in production
    logger.add(
        "logs/app.log",
        rotation="100 MB",
        retention="14 days",
        level="INFO",
        serialize=True,        # JSON lines for log aggregators
        enqueue=True,          # Thread-safe async logging
    )


__all__ = ["logger", "setup_logging"]
