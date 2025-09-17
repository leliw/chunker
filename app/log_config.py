import logging
import os
from datetime import datetime
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pythonjsonlogger.json import JsonFormatter as OrgJsonFormatter


class JsonFormatter(OrgJsonFormatter):
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None):
        # Format the timestamp as RFC 3339 with microsecond precision
        isoformat = datetime.fromtimestamp(record.created).isoformat()
        return f"{isoformat}Z"

class LogConfig(BaseSettings):
    """
    Pydantic settings model for logging configuration.
    Loads logging levels from environment variables prefixed with 'LOG_'.
    """

    model_config = SettingsConfigDict(env_prefix="LOG_")
    level: str = "INFO"
    """Root logging level (e.g., INFO, DEBUG)."""
    log_config: str = "DEBUG"
    """Logging level for this configuration module itself."""

    # Loggers
    log_config: str = "INFO"
    routers__pub_sub: str = "INFO"
    features__embeddings__embedding_service: str = "INFO"


_log = logging.getLogger(__name__)


def setup_logging():
    """Sets up the application's logging configuration.

    Chooses between structured (JSON) logging and plain text logging based on the presence
    of the 'OTEL_EXPORTER_OTLP_ENDPOINT' environment variable.
    Also configures logging levels for various loggers based on environment variables.    
    """
    if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        setup_structured_logging()
    else:
        setup_text_logging()

    # Load logging configuration from settings
    logconfig = LogConfig()
    for k, v in logconfig.model_dump().items():
        # Convert double underscores in setting names to dots for logger names
        name = k.replace("__", ".") if k != "level" else None
        logging.getLogger(name).setLevel(v)
        _log.debug("Logging %s -> %s", name, v)

    _log.debug("Logging configured")

def setup_text_logging() -> None:
    # Get the root logger
    root_logger = logging.getLogger()
    # Get or create a StreamHandler for console output
    ch = root_logger.handlers[0] if len(root_logger.handlers) > 0 else logging.StreamHandler()
    try:
        # Attempt to set FastAPI-like formatter using uvicorn's DefaultFormatter
        import uvicorn.logging

        formatter = uvicorn.logging.DefaultFormatter("%(levelprefix)s %(name)s: %(message)s")
    except ImportError:
        # Fallback to a standard formatter if uvicorn is not available
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Set the formatter for the handler
    ch.setFormatter(formatter)
    # Add the handler to the root logger
    logging.getLogger().addHandler(ch)

def setup_structured_logging() -> None:
    from opentelemetry.instrumentation.logging import LoggingInstrumentor

    LoggingInstrumentor().instrument()
    log_handler = logging.StreamHandler()
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(message)s %(otelTraceID)s %(otelSpanID)s %(otelTraceSampled)s",
        rename_fields={
            "levelname": "severity",
            "asctime": "timestamp",
            "otelTraceID": "logging.googleapis.com/trace",
            "otelSpanID": "logging.googleapis.com/spanId",
            "otelTraceSampled": "logging.googleapis.com/trace_sampled",
        },
    )
    log_handler.setFormatter(formatter)
    logging.basicConfig(
        level=logging.INFO,
        handlers=[log_handler],
    )