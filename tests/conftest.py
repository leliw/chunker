from config import ServerConfig
from dependencies import get_server_config
import main
import pytest
from fastapi import FastAPI

@pytest.fixture
def config() -> ServerConfig:
    config = ServerConfig()
    return config

@pytest.fixture
def app(config: ServerConfig) -> FastAPI:
    main.app.dependency_overrides[get_server_config] = lambda: config
    return main.app
