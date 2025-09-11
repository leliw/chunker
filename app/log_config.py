import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from log_context import ContextFilter


class LogConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_")
    level: str = "INFO"
    # Loggers
    log_config: str = "INFO"
    routers__pub_sub: str = "INFO"
    features__embeddings__embedding_service: str = "INFO"


_log = logging.getLogger(__name__)


def setup_logging():
    root_logger = logging.getLogger()
    ch = root_logger.handlers[0] if len(root_logger.handlers) > 0 else logging.StreamHandler()
    try:
        # Set FastAPI like formater
        import uvicorn.logging

        # Add context_info to the log format. It will be populated by ContextFilter.
        formatter = uvicorn.logging.DefaultFormatter("%(levelprefix)s %(name)s: %(context_info)s%(message)s")
    except ImportError:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(context_info)s%(message)s")
    ch.setFormatter(formatter)
    # Add the context filter to the handler.
    ch.addFilter(ContextFilter())
    logging.getLogger().addHandler(ch)

    logconfig = LogConfig()
    for k, v in logconfig.model_dump().items():
        name = k.replace("__", ".") if k != "level" else None
        logging.getLogger(name).setLevel(v)
        _log.debug("Logging %s -> %s", name, v)

    _log.debug("Logging configured")
