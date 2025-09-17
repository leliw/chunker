import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    """
    Sets up the application's logging configuration.

    It configures the root logger, attempts to use uvicorn's default formatter
    if available, and then sets logging levels for various modules based on
    the `LogConfig` settings.
    """
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