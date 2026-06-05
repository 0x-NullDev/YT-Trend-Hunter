"""
YT Trend Hunter - Logging Configuration
Centralized logging setup using loguru.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and redirect them to loguru.
    This ensures all logs (including from third-party libraries) use loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Redirect log record to loguru."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    Configure logging for the application.
    Sets up loguru with console and file handlers.
    """
    # Remove default handler
    logger.remove()

    # Console handler
    if settings.is_development:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=settings.LOG_LEVEL,
            colorize=False,
            backtrace=False,
            diagnose=False,
        )

    # File handler
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_path),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.LOG_LEVEL,
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
    )

    # JSON file handler for production
    if settings.is_production:
        json_log_path = log_path.with_suffix(".json")
        logger.add(
            str(json_log_path),
            format=lambda record: json.dumps(
                {
                    "timestamp": record["time"].isoformat(),
                    "level": record["level"].name,
                    "module": record["name"],
                    "function": record["function"],
                    "line": record["line"],
                    "message": record["message"],
                    "extra": record.get("extra", {}),
                }
            ),
            level=settings.LOG_LEVEL,
            rotation="100 MB",
            retention="30 days",
            compression="gz",
        )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set third-party loggers to WARNING
    for logger_name in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "sqlalchemy",
        "sqlalchemy.engine",
        "httpx",
        "httpcore",
        "urllib3",
        "elasticsearch",
        "aiocache",
        "celery",
        "praw",
        "pytrends",
    ):
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logger.info(f"Logging configured: level={settings.LOG_LEVEL}, file={settings.LOG_FILE}")
