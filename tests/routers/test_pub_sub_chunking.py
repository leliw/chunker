import time
import uuid

import main
import pytest
from ampf.gcp import GcpBlobStorage, GcpPubsubRequest, GcpSubscription, GcpTopic
from app_config import AppConfig
from dependencies import get_server_config
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from features.chunks.chunk_model import GcpFile
from log_config import setup_logging
from routers.chunks import ChunksRequest, ChunkWithEmbeddings
from conftest import client_factory
from app.routers import pub_sub


@pytest.fixture(scope="module")
def request_embedding_topic() -> GcpTopic:  # type: ignore
    topic_id = "chunker_unit_tests_" + uuid.uuid4().hex[:6]
    topic = GcpTopic(topic_id).create(exist_ok=True)
    yield topic  # type: ignore
    topic.delete()


@pytest.fixture(scope="module")
def request_embedding_subscription(request_embedding_topic: GcpTopic):
    subscription = request_embedding_topic.create_subscription(clazz=ChunkWithEmbeddings, exist_ok=True)
    yield subscription
    subscription.delete()


@pytest.fixture(scope="module")
def config(request_embedding_topic) -> AppConfig:
    config = AppConfig()
    config.chunk_embedding_requests_topic = request_embedding_topic.topic_id
    return config


@pytest.fixture(scope="module")
def app(config: AppConfig) -> FastAPI:
    main.app.dependency_overrides[get_server_config] = lambda: config
    return main.app


@pytest.fixture(scope="module")
def topic():
    topic_id = "chunker_unit_tests_" + uuid.uuid4().hex[:6]
    topic = GcpTopic(topic_id).create(exist_ok=True)
    yield topic
    topic.delete()


@pytest.fixture(scope="module")
def subscription(topic: GcpTopic):
    subscription_id = f"{topic.topic_id}-sub"
    subscription = topic.create_subscription(subscription_id, clazz=ChunkWithEmbeddings, exist_ok=True)
    yield subscription
    subscription.delete()


@pytest.fixture(scope="module")
def client(app: FastAPI):
    app.include_router(pub_sub.router, prefix="/pub-sub")
    setup_logging()
    with TestClient(app) as client:
        yield client


def test_short_text_chunking(topic: GcpTopic, subscription: GcpSubscription, client: TestClient):
    # Given: Message payload
    payload = ChunksRequest(job_id=uuid.uuid4(), text="xxx")
    # And: A fake request pushed from a subscription
    req = GcpPubsubRequest.create(payload, {"response_topic": topic.topic_id})
    # When: The request is posted
    response = client.post("/pub-sub/requests", json=req.model_dump())
    # Then: Response is OK
    assert response.status_code == status.HTTP_200_OK
    # And: Chunk is received (with embedding)
    chunk = subscription.receive_first_payload(lambda p: p.job_id == payload.job_id)
    assert chunk
    assert chunk.chunk_index == 0
    assert chunk.total_chunks == 1
    assert chunk.text == chunk.text
    assert chunk.embedding


def test_long_text_chunking(
    topic: GcpTopic,
    subscription: GcpSubscription,
    request_embedding_subscription: GcpSubscription,
    config: AppConfig,
):
    # Given: Message payload with long text
    with open("./tests/data/long_pl.txt", "r") as f:
        payload = ChunksRequest(job_id=uuid.uuid4(), text=f.read())
    # And: A fake request pushed from a subscription
    req = GcpPubsubRequest.create(payload, response_topic=topic.topic_id)
    with client_factory(config) as client:
        # And: Pub/Sub push is emulated
        with request_embedding_subscription.run_push_emulator(client, "/pub-sub/requests/embeddings") as sub_emulator:
            # When: The request is posted
            client.post("/pub-sub/requests", 200, json=req)
            # And: All forwarded messages are processed
            while not sub_emulator.isfinished(timeout=60, expected_responses=9):
                time.sleep(0.1)
        # And: Payloads between steps don't have embedding
        payloads = sub_emulator.get_payloads()
        assert not any(p.embedding for p in payloads)
        # And: At the end a chunk is received with embedding
        chunk = subscription.receive_first_payload(lambda p: p.job_id == payload.job_id)
        assert chunk
        assert chunk.total_chunks == 9
        assert chunk.embedding


@pytest.fixture(scope="module")
def blob_storage_md(gcp_bucket_name: str):
    bs = GcpBlobStorage(uuid.uuid4().hex, None, "text/markdown", gcp_bucket_name)
    yield bs
    bs.drop()


def test_input_file_chunking(
    topic: GcpTopic, subscription: GcpSubscription, client: TestClient, blob_storage_md: GcpBlobStorage
):
    # Given: A markdown file stored in Cloud Storage
    blob_storage_md.upload_blob("test.md", "xxx".encode())
    # And: Message payload with this file
    payload = ChunksRequest(
        job_id=uuid.uuid4(),
        input_file=GcpFile(
            bucket=blob_storage_md._bucket.name,
            name=f"{blob_storage_md.collection_name}/test.md",
        ),
    )
    # And: A fake request pushed from a subscription
    req = GcpPubsubRequest.create(payload, {"response_topic": topic.topic_id})

    # When: The request is posted
    response = client.post("/pub-sub/requests", json=req.model_dump())

    # Then: Response is OK
    assert response.status_code == status.HTTP_200_OK
    # And: Chunk is received (with embedding)
    chunk = subscription.receive_first_payload(lambda p: p.job_id == payload.job_id)
    assert chunk
    assert chunk.chunk_index == 0
    assert chunk.total_chunks == 1
    assert chunk.text == chunk.text
    assert chunk.embedding
