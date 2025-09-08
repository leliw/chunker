import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import embeddings
from app.routers.embeddings import EmbeddingResponse


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
    assert "ipipan/silver-retriever-base-v1.1" in r


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
    r = EmbeddingResponse.model_validate(response.json())
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The response is list of embeddings
    assert isinstance(r, EmbeddingResponse)
    assert len(r.embedding) > 0
    # And: The response is a list of floats
    assert all(isinstance(i, float) for i in r.embedding)
    # And: It is different from regular embeddings
    response = client.post("/api/embeddings/generate", json={"text": text})
    r2 = response.json()
    assert r != r2


@pytest.mark.parametrize(
    ["model_name", "length"],
    [
        ("ipipan/silver-retriever-base-v1.1", 768),
        ("Qwen/Qwen3-Embedding-0.6B", 1024),
    ],
)
def test_generate_embeddings_by_model_name(client, model_name, length):
    # Given: A model name and some text
    text = "This is a test sentence."
    # When: A POST request is made to /api/embeddings/generate
    response = client.post("/api/embeddings/generate", json={"text": text, "embedding_model_name": model_name})
    r = response.json()
    # Then: Embedding size is 768 or 1024
    assert len(r) == length


@pytest.mark.parametrize(
    ["language", "length"],
    [
        ("pl", 768),
        ("en", 1024),
    ],
)
def test_generate_embeddings_by_language(client, language, length):
    # Given: A language and some text
    text = "This is a test sentence."
    # When: A POST request is made to /api/embeddings/generate
    response = client.post("/api/embeddings/generate", json={"text": text, "language": language})
    r = response.json()
    # Then: Embedding size is 768 or 1024
    assert len(r) == length


@pytest.mark.parametrize(
    ["language", "text", "length"],
    [
        ("pl", "Kto był pierwszym królem Polski?", 768),
        ("en", "Who was the first king of Poland?", 1024),
    ],
)
def test_generate_query_embeddings_by_language(client, language, text, length):
    # When: A POST request is made to /api/embeddings/generate/query
    response = client.post("/api/embeddings/generate/query", json={"text": text, "language": language})
    r = response.json()
    # Then: Embedding size is 768 or 1024
    assert len(r["embedding"]) == length


@pytest.mark.parametrize(
    ["language", "title", "text", "length"],
    [
        ("pl", "Bolesław Chrobry", "Bolesław Chrobry był pierwszym królem Polski.", 768),
        ("en", "Bolesław the Brave", "Bolesław the Brave was the first king of Poland.", 1024),
    ],
)
def test_generate_passage_embeddings_by_language(client, language, title, text, length):
    # When: A POST request is made to /api/embeddings/generate/passage
    response = client.post("/api/embeddings/generate/passage", json={"title": title, "text": text, "language": language})
    r = response.json()
    # Then: Embedding size is 768 or 1024
    assert len(r["embedding"]) == length