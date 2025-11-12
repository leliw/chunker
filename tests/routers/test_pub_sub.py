import base64
import uuid

from ampf.base import BaseAsyncFactory
from ampf.gcp import GcpPubsubMessage, GcpPubsubRequest, GcpPubsubResponse
from ampf.testing import ApiTestClient, MockMethod
from app_config import AppConfig
from routers.chunks import ChunksRequest, ChunkWithEmbeddings
from conftest import client_factory



def test_delivery_push_with_response_topic(client: ApiTestClient, mock_method: MockMethod):
    # Patch the PublisherClient.publish method to mock GCP publish
    mock_publish = mock_method(BaseAsyncFactory.publish_message)

    # Given: a Pub/Sub message with response_topic
    job_id = uuid.uuid4()
    reqest = ChunksRequest(job_id=job_id, text="xxx")
    response_topic = "chunks"
    message = GcpPubsubRequest.create(reqest, response_topic=response_topic, sender_id="unittests")
    # When: A POST message to /pub-sub
    r = client.post_typed("/pub-sub/requests", 200, GcpPubsubResponse, json=message)
    # Then: The message is acknowledged
    assert r.status == "acknowledged"
    # And: publish was called with correct arguments
    mock_publish.assert_called()
    args, _ = mock_publish.call_args
    resp_topic = args[0]
    assert resp_topic.endswith(response_topic)
    data: ChunkWithEmbeddings = args[1]
    assert data.chunk_index == 0
    assert data.text == reqest.text
    assert data.embedding


def test_delivery_push_without_response_topic(mock_method: MockMethod):
    # Patch the PublisherClient.publish method to mock GCP publish
    mock_publish = mock_method(BaseAsyncFactory.publish_message)
    # Given: a Pub/Sub message without response_topic and sender_id
    job_id = uuid.uuid4()
    reqest = ChunksRequest(job_id=job_id, text="xxx")
    message_id = uuid.uuid4().hex
    message = GcpPubsubRequest(
        message=GcpPubsubMessage(
            messageId=message_id,
            data=base64.b64encode(reqest.model_dump_json().encode("utf-8")).decode("utf-8"),
        ),
        subscription="test/subscription",
    )
    # And: chunks_resoponse_topic is set in config
    config = AppConfig(chunking_responses_topic="chunks2")
    with client_factory(config) as client:
        # When: A POST message to /pub-sub
        r = client.post_typed("/pub-sub/requests", 200, GcpPubsubResponse, json=message)
        # Then: The message is acknowledged
        assert r.status == "acknowledged"
        # And: publish was called with correct arguments
        mock_publish.assert_called_once()
        args, _ = mock_publish.call_args
        resp_topic = args[0]
        assert resp_topic.endswith(config.chunking_responses_topic)
        data: ChunkWithEmbeddings = args[1]
        assert data.chunk_index == 0
        assert data.text == reqest.text
        assert data.embedding


def test_delivery_push_with_sender_id(mock_method: MockMethod):
    # Patch the PublisherClient.publish method to mock GCP publish
    mock_publish = mock_method(BaseAsyncFactory.publish_message)
    # Given: a Pub/Sub message with sender_id
    reqest = ChunksRequest(text="xxx")
    sender_id = "unittests"
    message = GcpPubsubRequest.create(reqest, sender_id=sender_id)
    # And: chunks_resoponse_topic is set in config
    config = AppConfig(chunking_responses_topic="chunks2")
    with client_factory(config) as client:
        # When: A POST message to /pub-sub
        r = client.post_typed("/pub-sub/requests", 200, GcpPubsubResponse, json=message)
        # Then: The message is acknowledged
        assert r.status == "acknowledged"
        # And: publish was called with correct arguments
        mock_publish.assert_called_once()
        args, attrs = mock_publish.call_args
        resp_topic = args[0]
        assert resp_topic.endswith(config.chunking_responses_topic)
        # And: Sendder_id attribute is set
        assert sender_id == attrs.get("sender_id")
        data: ChunkWithEmbeddings = args[1]
        assert data.chunk_index == 0
        assert data.text == reqest.text
        assert data.embedding
