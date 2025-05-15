# content of /home/marcin/src/chunker/tests/app/test_main.py
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from config import ServerConfig
from dependencies import get_server_config


@pytest.fixture(autouse=True)
def mock_embedding_service_dependencies(mocker):
    """
    Mocks dependencies for EmbeddingService to prevent actual model loading
    during these web layer tests. This fixture applies to all tests in this module.
    """
    # Mock SentenceTransformer to prevent actual model loading
    mocker.patch(
        "app.features.embeddings.embedding_service.SentenceTransformer", autospec=True
    )
    # Mock get_models to prevent os.listdir errors and ensure a model name is returned
    # This is called if config.model_name is not set.
    mocker.patch(
        "app.features.embeddings.embedding_service.EmbeddingService.get_models",
        return_value=["mock_model_org/mock_model_name"],  # Must return a non-empty list
        autospec=True,
    )


@pytest.fixture
def client(app):
    """
    Provides a TestClient instance for making requests to the app.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clear_dependency_overrides_after_test(app):
    """
    Ensures that any dependency overrides are cleared after each test,
    maintaining test isolation. This fixture applies to all tests in this module.
    """
    yield
    app.dependency_overrides = {}


def test_global_api_key_valid_when_required(app: FastAPI, client: TestClient, caplog):
    """
    Tests that a valid API key grants access when an API key is configured.
    """
    # Arrange
    test_api_key = "test_secret_key"
    # Override the ServerConfig dependency to simulate an API key being set
    app.dependency_overrides[get_server_config] = lambda: ServerConfig(
        api_key=test_api_key, version="test_v"
    )

    # Act
    # We make a request to an existing simple endpoint, e.g., /api/config/
    # This endpoint is protected by the global verify_api_key dependency.
    with caplog.at_level(logging.DEBUG, logger="dependencies"):
        response = client.get("/api/config", headers={"X-API-Key": test_api_key})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "version": "test_v"
    }  # Assuming /api/config/ returns ClientConfig
    assert "API key verified" in caplog.text


def test_global_api_key_invalid_when_required(app: FastAPI,client: TestClient, caplog):
    """
    Tests that an invalid API key results in a 403 Forbidden error.
    """
    # Arrange
    test_api_key = "test_secret_key"
    app.dependency_overrides[get_server_config] = lambda: ServerConfig(
        api_key=test_api_key
    )

    # Act
    with caplog.at_level(logging.WARNING, logger="dependencies"):
        response = client.get("/api/config/", headers={"X-API-Key": "wrong_key"})

    # Assert
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid API key"}
    assert "Invalid API key" in caplog.text


def test_global_api_key_missing_when_required(app: FastAPI,client: TestClient, caplog):
    """
    Tests that a missing API key results in a 403 Forbidden error.
    """
    # Arrange
    test_api_key = "test_secret_key"
    app.dependency_overrides[get_server_config] = lambda: ServerConfig(
        api_key=test_api_key
    )

    # Act
    with caplog.at_level(logging.WARNING, logger="dependencies"):
        response = client.get("/api/config/")  # No X-API-Key header

    # Assert
    assert response.status_code == 403
    assert response.json() == {"detail": "Missing API key"}
    assert "Missing API key" in caplog.text


def test_global_api_key_not_required(app: FastAPI,client: TestClient, caplog):
    """
    Tests that access is granted if no API key is configured on the server,
    even if no key is provided in the request.
    """
    # Arrange
    # Override ServerConfig to simulate no API key being set (api_key=None)
    app.dependency_overrides[get_server_config] = lambda: ServerConfig(
        api_key=None, version="test_v_no_key"
    )

    # Act
    with caplog.at_level(logging.DEBUG, logger="dependencies"):
        response_no_header = client.get("/api/config")
        response_with_header = client.get(
            "/api/config", headers={"X-API-Key": "any_key_is_ignored"}
        )

    # Assert
    assert response_no_header.status_code == 200
    assert response_no_header.json() == {"version": "test_v_no_key"}

    assert response_with_header.status_code == 200
    assert response_with_header.json() == {"version": "test_v_no_key"}

    # Check that the "API key not required" message is logged for both cases
    assert caplog.text.count("API key not required") >= 2
