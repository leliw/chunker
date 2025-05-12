import pytest
from dependencies import lifespan
from fastapi import FastAPI


@pytest.fixture
def app() -> FastAPI:
    return FastAPI(lifespan=lifespan)