import pytest
from ampf.testing import PubSubManager
from app_config import AppConfig
from features.chunks.chunk_model import ChunkWithEmbeddings, ChunksRequest

from tests.conftest import client_factory


@pytest.mark.asyncio
async def test_chunking_requests(pubsub_manager: PubSubManager):
    config = AppConfig(
        chunking_requests_topic="test-req",
        chunking_responses_topic="test_resp",
        chunk_embedding_requests_topic="test-e-req",
    )
    assert config.chunking_requests_topic
    assert config.chunking_responses_topic
    pubsub_manager.prepare_resources(config, prepare_topic_subscriptions=True)
    sub_req = pubsub_manager.prepare_topic_subscription(config.chunking_requests_topic, clazz=ChunksRequest)
    sub_resp = pubsub_manager.prepare_topic_subscription(config.chunking_responses_topic, clazz=ChunkWithEmbeddings)
    with client_factory(config):
        # Given: A chunks request
        req = ChunksRequest(text="Pierwszym królem Polski był Bolesław Chrobry")
        # When: The chunks request is published
        pubsub_manager.publish(config.chunking_requests_topic, req)
        await sub_req.wait_until_empty()
        # Then: Chunks are returned
        chunk = sub_resp.receive_first_payload(lambda p: True)
        assert chunk
        assert chunk.chunk_index == 0
        assert chunk.text == req.text


@pytest.mark.asyncio
async def test_chunk_embedding_requests(pubsub_manager: PubSubManager):
    config = AppConfig(
        chunking_requests_topic="test2-req",
        chunking_responses_topic="test2_resp",
        chunk_embedding_requests_topic="test2-e-req",
    )
    assert config.chunk_embedding_requests_topic
    assert config.chunking_responses_topic
    pubsub_manager.prepare_resources(config, prepare_topic_subscriptions=True)
    sub_req = pubsub_manager.prepare_topic_subscription(
        config.chunk_embedding_requests_topic, clazz=ChunkWithEmbeddings
    )
    sub_resp = pubsub_manager.prepare_topic_subscription(config.chunking_responses_topic, clazz=ChunkWithEmbeddings)
    with client_factory(config):
        # Given: A chunks request
        req = ChunkWithEmbeddings(
            text="Pierwszym królem Polski był Bolesław Chrobry",
            chunk_index=0,
            total_chunks=1,
            language="pl",
            embedding_model_name="ipipan/silver-retriever-base-v1.1",
            embedding=[],
        )
        # When: The chunks request is published
        pubsub_manager.publish(config.chunk_embedding_requests_topic, req, response_topic=config.chunking_responses_topic)
        await sub_req.wait_until_empty()
        # Then: Chunks are returned
        chunk = sub_resp.receive_first_payload(lambda p: True)
        assert chunk
        assert chunk.chunk_index == 0
        assert chunk.text == req.text
        assert chunk.embedding
