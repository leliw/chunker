import main
import pytest
from app_config import AppConfig
from dependencies import get_server_config
from fastapi import FastAPI


@pytest.fixture
def config() -> AppConfig:
    config = AppConfig()
    return config


@pytest.fixture
def app(config: AppConfig) -> FastAPI:
    main.app.dependency_overrides[get_server_config] = lambda: config
    return main.app


@pytest.fixture(scope="session")
def gcp_bucket_name() -> str:
    return "unit-tests-001"
