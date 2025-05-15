import main
import pytest
from fastapi import FastAPI


@pytest.fixture
def app() -> FastAPI:
    return main.app
