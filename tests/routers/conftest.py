import pytest
from config import ServerConfig
from dependencies import get_server_config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app as main_app


@pytest.fixture
def app(config: ServerConfig):
    app = main_app
    app.dependency_overrides[get_server_config] = lambda: config
    return app


@pytest.fixture
def client(app: FastAPI):
    with TestClient(app) as client:
        yield client
