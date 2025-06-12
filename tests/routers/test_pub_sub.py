import base64
import re
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import pub_sub
from log_config import setup_logging


@pytest.fixture
def client(app: FastAPI):
    app.include_router(pub_sub.router, prefix="/pub-sub")
    setup_logging()
    with TestClient(app) as client:
        yield client


def test_get_client_config(client):
    # Given: a Pub/Sub message
    message_id = uuid.uuid4().hex
    message = pub_sub.PushRequest(
        message=pub_sub.PubsubMessage(
            messageId=message_id,
            data=base64.b64encode(b"xxx").decode("utf-8")),
        subscription="test/subscription",
    )
    # When: A POST message to /pub-sub
    response = client.post("/pub-sub", json=message.model_dump())
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The message is acknowledged
    assert r["status"] == "acknowledged"
