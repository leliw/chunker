import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_")
    level: str = "INFO"
    log_config: str = "INFO"
    # Loggers
    routers__pub_sub: str = "INFO"


_log = logging.getLogger(__name__)


def setup_logging():
    root_logger = logging.getLogger()
    ch = root_logger.handlers[0] if len(root_logger.handlers) > 0 else logging.StreamHandler()
    try:
        # Set FastAPI like formater
        import uvicorn.logging

        formatter = uvicorn.logging.DefaultFormatter("%(levelprefix)s %(name)s: %(message)s")
    except ImportError:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logging.getLogger().addHandler(ch)

    logconfig = LogConfig()
    for k, v in logconfig.model_dump().items():
        name = k.replace("__", ".") if k != "level" else None
        logging.getLogger(name).setLevel(v)
        _log.debug("Logging %s -> %s", name, v)

    _log.debug("Logging configured")
