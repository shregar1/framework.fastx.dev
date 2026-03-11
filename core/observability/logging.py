"""
Structured Logging Module.

Provides structured JSON logging with context propagation,
request correlation, and log level management.
"""

import contextvars
import json
import sys
from datetime import datetime
from typing import Any, Optional

from loguru import logger

# Context variables for request-scoped logging
_request_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
_user_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)
_tenant_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "tenant_id", default=None
)
_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_id", default=None
)
_extra_context: contextvars.ContextVar[dict] = contextvars.ContextVar(
    "extra_context", default={}
)


def set_log_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Set logging context for the current request.

    Args:
        request_id: Request correlation ID.
        user_id: Current user ID.
        tenant_id: Current tenant ID.
        trace_id: Distributed trace ID.
        **kwargs: Additional context values.
    """
    if request_id:
        _request_id.set(request_id)
    if user_id:
        _user_id.set(user_id)
    if tenant_id:
        _tenant_id.set(tenant_id)
    if trace_id:
        _trace_id.set(trace_id)
    if kwargs:
        current = _extra_context.get()
        _extra_context.set({**current, **kwargs})


def get_log_context() -> dict[str, Any]:
    """Get current logging context."""
    context = {}
    if _request_id.get():
        context["request_id"] = _request_id.get()
    if _user_id.get():
        context["user_id"] = _user_id.get()
    if _tenant_id.get():
        context["tenant_id"] = _tenant_id.get()
    if _trace_id.get():
        context["trace_id"] = _trace_id.get()
    context.update(_extra_context.get())
    return context


def clear_log_context() -> None:
    """Clear logging context."""
    _request_id.set(None)
    _user_id.set(None)
    _tenant_id.set(None)
    _trace_id.set(None)
    _extra_context.set({})


def json_formatter(record: dict) -> str:
    """
    Format log record as JSON.

    Includes context from context variables and extra fields.
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "logger": record["name"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add context
    log_entry.update(get_log_context())

    # Add extra fields from record
    if record.get("extra"):
        for key, value in record["extra"].items():
            if key not in log_entry and not key.startswith("_"):
                log_entry[key] = value

    # Add exception info if present
    if record.get("exception"):
        log_entry["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
            "traceback": record["exception"].traceback,
        }

    return json.dumps(log_entry) + "\n"


class StructuredLogger:
    """
    Structured logger with context propagation.

    Wraps loguru to provide structured JSON logging with
    automatic context inclusion.

    Usage:
        logger = StructuredLogger("my_service")
        logger.info("Processing order", order_id="123", amount=99.99)

        # With context
        set_log_context(request_id="req-123", user_id="user-456")
        logger.info("User action")  # Automatically includes context
    """

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        json_output: bool = True,
        include_caller: bool = True,
    ):
        """
        Initialize structured logger.

        Args:
            name: Logger name (included in all log entries).
            level: Minimum log level.
            json_output: Output logs as JSON.
            include_caller: Include caller info (module, function, line).
        """
        self._name = name
        self._level = level
        self._json_output = json_output
        self._include_caller = include_caller
        self._logger = logger.bind(name=name)

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        """Internal logging method."""
        bound_logger = self._logger.bind(**kwargs)
        getattr(bound_logger, level.lower())(message)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._log("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._logger.bind(**kwargs).exception(message)

    def bind(self, **kwargs: Any) -> "StructuredLogger":
        """Create a new logger with additional bound context."""
        new_logger = StructuredLogger(
            self._name,
            self._level,
            self._json_output,
            self._include_caller,
        )
        new_logger._logger = self._logger.bind(**kwargs)
        return new_logger


def configure_logging(
    level: str = "INFO",
    json_output: bool = True,
    log_file: Optional[str] = None,
    rotation: str = "100 MB",
    retention: str = "7 days",
) -> None:
    """
    Configure global logging settings.

    Args:
        level: Minimum log level.
        json_output: Output logs as JSON.
        log_file: Optional file path for log output.
        rotation: Log rotation size/time.
        retention: Log retention period.
    """
    # Remove default handler
    logger.remove()

    # Console handler
    if json_output:
        logger.add(
            sys.stdout,
            format=json_formatter,
            level=level,
            serialize=False,
        )
    else:
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level=level,
        )

    # File handler
    if log_file:
        logger.add(
            log_file,
            format=json_formatter if json_output else "{time} | {level} | {message}",
            level=level,
            rotation=rotation,
            retention=retention,
            compression="gz",
        )
