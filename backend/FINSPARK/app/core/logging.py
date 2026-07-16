import contextvars
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict

# Context variables for trace correlation
correlation_id_ctx = contextvars.ContextVar("correlation_id", default="")
trace_id_ctx = contextvars.ContextVar("trace_id", default="")


class StructuredJSONFormatter(logging.Formatter):
    """
    Custom logging formatter for outputting structured JSON logs with security metadata.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get(),
            "trace_id": trace_id_ctx.get(),
        }

        # Include standard exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include extra attributes passed in logging call
        for key, val in record.__dict__.items():
            if key not in {
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "levelname", "levelno", "lineno", "module", "msecs",
                "msg", "name", "pathname", "process", "processName", "relativeCreated",
                "stack_info", "thread", "threadName"
            }:
                log_data[key] = val

        return json.dumps(log_data)


def setup_structured_logging(level: int = logging.INFO) -> None:
    """
    Configures the root logger to output structured JSON to standard out.
    """
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid duplicate output formatting
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredJSONFormatter())
    
    root_logger.addHandler(console_handler)
    root_logger.setLevel(level)

    # Silence noisy dependencies in dev logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# Initialize logging immediately
setup_structured_logging()
logger = logging.getLogger("finspark_pam")
