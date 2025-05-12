import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import config


@pytest.fixture
def client(app: FastAPI):
    app.include_router(config.router, prefix="/api/config")
    with TestClient(app) as client:
        yield client


def test_get_client_config(client):
    # When: A GET request is made to /api/config
    response = client.get("/api/config")
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The response has "version" and "google_oauth_client_id"
    assert 1 == len(r)
    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, r["version"])
