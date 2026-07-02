"""
Application-wide logging configuration.

Called once from main.py's startup event. Every module should get its own
named logger via `logging.getLogger(__name__)` rather than using print()
or the root logger directly.
"""

import logging
import sys

from backend.config.settings import Settings

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(settings: Settings) -> None:
    """Configure root logging handlers and level from application settings."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if setup_logging is ever called more than once
    # (e.g. under a test runner that re-imports the app).
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet down noisy third-party loggers unless we're actively debugging.
    if level > logging.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging configured | environment=%s | level=%s", settings.ENVIRONMENT, settings.LOG_LEVEL
    )