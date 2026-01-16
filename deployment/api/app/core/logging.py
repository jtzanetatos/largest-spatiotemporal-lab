from __future__ import annotations

import logging
import os
import sys
from contextvars import ContextVar

from loguru import logger

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class InterceptHandler(logging.Handler):
    """Redirect stdlib logging (uvicorn, fastapi, etc.) into loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.bind(request_id=request_id_var.get()).opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, record.getMessage())


def configure_logging() -> None:
    """
    Container-friendly logging:
    - stdout sink
    - optional JSON format via LOG_FORMAT=json
    - unify uvicorn/stdlib logs into loguru
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "text").lower()  # "text" or "json"

    logger.remove()

    if log_format == "json":
        fmt = (
            '{{"time":"{time:YYYY-MM-DDTHH:mm:ss.SSSZ}",'
            '"level":"{level}",'
            '"message":{message!r},'
            '"request_id":"{extra[request_id]}",'
            '"module":"{name}",'
            '"line":{line}}}'
        )
    else:
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "rid={extra[request_id]} | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

    logger.add(sys.stdout, level=log_level, format=fmt, backtrace=False, diagnose=False)

    intercept = InterceptHandler()
    logging.root.handlers = [intercept]
    logging.root.setLevel(log_level)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        _logger = logging.getLogger(name)
        _logger.handlers = [intercept]
        _logger.propagate = False
        _logger.setLevel(log_level)

    logger.configure(extra={"request_id": request_id_var.get()})
