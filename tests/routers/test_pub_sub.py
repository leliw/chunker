import base64
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.routers import pub_sub
from config import ServerConfig
from log_config import setup_logging
from routers.chunks import ChunkWithEmebeddings, ChunksRequest


@pytest.fixture
def client(app: FastAPI):
    app.include_router(pub_sub.router, prefix="/pub-sub")
    setup_logging()
    with TestClient(app) as client:
        yield client


def test_delivery_push_with_response_topic(client):
    # Given: a Pub/Sub message with response_topic
    job_id = uuid.uuid4()
    reqest = ChunksRequest(job_id=job_id, text="xxx")
    message_id = uuid.uuid4().hex
    response_topic = "chunks"
    message = pub_sub.PushRequest(
        message=pub_sub.PubsubMessage(
            messageId=message_id,
            attributes={"response_topic": response_topic},
            data=base64.b64encode(reqest.model_dump_json().encode("utf-8")).decode("utf-8"),
        ),
        subscription="test/subscription",
    )
    # Patch the PublisherClient.publish method to mock GCP publish
    with patch("google.cloud.pubsub_v1.PublisherClient.publish") as mock_publish:
        mock_future = type("MockFuture", (), {"result": lambda self: "mocked-message-id"})()
        mock_publish.return_value = mock_future
        # When: A POST message to /pub-sub
        response = client.post("/pub-sub/requests", json=message.model_dump())
        r = response.json()
        # Then: The response status code is 200
        assert 200 == response.status_code
        # And: The message is acknowledged
        assert r["status"] == "acknowledged"
        # And: publish was called with correct arguments
        mock_publish.assert_called()
        args, _ = mock_publish.call_args
        resp_topic = args[0]
        assert resp_topic.endswith(response_topic)
        bdata: bytes = args[1]
        assert bdata
        data = ChunkWithEmebeddings.model_validate_json(bdata.decode("utf-8"))
        assert data.chunk_index == 0
        assert data.text == reqest.text
        assert data.embedding


def test_delivery_push_without_response_topic(config: ServerConfig, client):
    # Given: a Pub/Sub message without response_topic and sender_id
    job_id = uuid.uuid4()
    reqest = ChunksRequest(job_id=job_id, text="xxx")
    message_id = uuid.uuid4().hex
    message = pub_sub.PushRequest(
        message=pub_sub.PubsubMessage(
            messageId=message_id,
            data=base64.b64encode(reqest.model_dump_json().encode("utf-8")).decode("utf-8"),
        ),
        subscription="test/subscription",
    )
    # And: chunks_resoponse_topic is set in config
    config.chunks_response_topic = "chunks2"
    # Patch the PublisherClient.publish method to mock GCP publish
    with patch("google.cloud.pubsub_v1.PublisherClient.publish") as mock_publish:
        mock_future = type("MockFuture", (), {"result": lambda self: "mocked-message-id"})()
        mock_publish.return_value = mock_future
        # When: A POST message to /pub-sub
        response = client.post("/pub-sub/requests", json=message.model_dump())
        r = response.json()
        # Then: The response status code is 200
        assert 200 == response.status_code
        # And: The message is acknowledged
        assert r["status"] == "acknowledged"
        # And: publish was called with correct arguments
        mock_publish.assert_called_once()
        args, _ = mock_publish.call_args
        resp_topic = args[0]
        assert resp_topic.endswith(config.chunks_response_topic)
        bdata: bytes = args[1]
        assert bdata
        data = ChunkWithEmebeddings.model_validate_json(bdata.decode("utf-8"))
        assert data.chunk_index == 0
        assert data.text == reqest.text
        assert data.embedding


def test_delivery_push_with_sender_id(config: ServerConfig, client):
    # Given: a Pub/Sub message with sender_id
    job_id = uuid.uuid4()
    reqest = ChunksRequest(job_id=job_id, text="xxx")
    message_id = uuid.uuid4().hex
    sender_id = "unittests"
    message = pub_sub.PushRequest(
        message=pub_sub.PubsubMessage(
            messageId=message_id,
            attributes={"sender_id": sender_id},
            data=base64.b64encode(reqest.model_dump_json().encode("utf-8")).decode("utf-8"),
        ),
        subscription="test/subscription",
    )
    # And: chunks_resoponse_topic is set in config
    config.chunks_response_topic = "chunks2"
    # Patch the PublisherClient.publish method to mock GCP publish
    with patch("google.cloud.pubsub_v1.PublisherClient.publish") as mock_publish:
        mock_future = type("MockFuture", (), {"result": lambda self: "mocked-message-id"})()
        mock_publish.return_value = mock_future
        # When: A POST message to /pub-sub
        response = client.post("/pub-sub/requests", json=message.model_dump())
        r = response.json()
        # Then: The response status code is 200
        assert 200 == response.status_code
        # And: The message is acknowledged
        assert r["status"] == "acknowledged"
        # And: publish was called with correct arguments
        mock_publish.assert_called_once()
        args, attrs = mock_publish.call_args
        resp_topic = args[0]
        assert resp_topic.endswith(config.chunks_response_topic)
        # And: Sendder_id attribute is set
        assert sender_id == attrs.get("sender_id")
        bdata: bytes = args[1]
        assert bdata
        data = ChunkWithEmebeddings.model_validate_json(bdata.decode("utf-8"))
        assert data.chunk_index == 0
        assert data.text == reqest.text
        assert data.embedding
