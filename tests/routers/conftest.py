from contextlib import contextmanager
import pytest
from ampf.testing import ApiTestClient
from app_config import AppConfig
from dependencies import get_server_config, lifespan
from fastapi import FastAPI
from main import app as main_app


@pytest.fixture
def app(config: AppConfig):
    app = main_app
    app.dependency_overrides[get_server_config] = lambda: config
    return app


@pytest.fixture
def client(app: FastAPI):
    with ApiTestClient(app) as client:
        yield client
