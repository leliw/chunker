from contextlib import contextmanager

import main
import pytest
from ampf.base import BaseAsyncFactory
from ampf.testing import ApiTestClient as AmpfApiTestClient
from app_config import AppConfig
from dependencies import get_server_config, lifespan
from fastapi import FastAPI
from main import app as main_app


class ApiTestClient(AmpfApiTestClient):
    async def publish_message(self, topic: str, message: str, **kwargs) -> str:
        async_factory: BaseAsyncFactory = self.app.state.app_state.async_factory  # type: ignore
        return await async_factory.publish_message(topic, message, **kwargs)


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


@contextmanager
def client_factory(config):
    # Reconfigure the lifespan to use the test server config
    main_app.router.lifespan_context = lifespan(config)
    with ApiTestClient(main_app) as client:
        yield client
