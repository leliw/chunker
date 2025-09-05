import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import embeddings


@pytest.fixture
def client(app: FastAPI):
    app.include_router(embeddings.router, prefix="/api/embeddings")
    with TestClient(app) as client:
        yield client


def test_get_models(client):
    # When: A GET request is made to /api/config
    response = client.get("/api/embeddings/models")
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The response is list of models
    assert isinstance(r, list)

def test_generate_embeddings(client):
    # Given: A model name and some text
    text = "This is a test sentence."
    # When: A POST request is made to /api/embeddings/generate
    response = client.post("/api/embeddings/generate", json={"text": text})
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The response is list of embeddings
    assert isinstance(r, list)
    assert len(r) > 0
    # And: The response is a list of floats
    assert all(isinstance(i, float) for i in r)

def test_generate_query_embeddings(client):
    # Given: A model name and some text
    text = "This is a test sentence."
    # When: A POST request is made to /api/embeddings/generate/query
    response = client.post("/api/embeddings/generate/query", json={"text": text})
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The response is list of embeddings
    assert isinstance(r, list)
    assert len(r) > 0
    # And: The response is a list of floats
    assert all(isinstance(i, float) for i in r)
    # And: It is different from regular embeddings
    response = client.post("/api/embeddings/generate", json={"text": text})
    r2 = response.json()
    assert r != r2