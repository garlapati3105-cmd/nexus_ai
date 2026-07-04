"""
Nexus AI — Structured Logging
Provides a configured logger for all backend modules.
"""
import logging
import sys
from app.core.config import get_settings


def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance for the given module name."""
    settings = get_settings()
    logger = logging.getLogger(f"nexus.{name}")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    return logger
