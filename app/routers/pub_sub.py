import logging
from typing import AsyncIterator, Dict, Iterator, Optional

from ampf.gcp import GcpPubsubRequest, gcp_pubsub_push_handler
from dependencies import ChunkServiceDep, ConfigDep, EmbeddingServiceDep
from fastapi import APIRouter
from pydantic import BaseModel
from routers.chunks import ChunksRequest, ChunkWithEmebeddings

_log = logging.getLogger(__name__)

router = APIRouter(tags=["Pub/Sub Push"])


class PubsubMessage(BaseModel):
    messageId: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    data: str
    publishTime: Optional[str] = None


class PushRequest(BaseModel):
    message: PubsubMessage
    subscription: str


@router.post("/requests")
@gcp_pubsub_push_handler()
def handle_push(
    config: ConfigDep,
    chunk_service: ChunkServiceDep,
    embedding_service: EmbeddingServiceDep,
    request: GcpPubsubRequest,
    payload: ChunksRequest,
) -> Iterator[ChunkWithEmebeddings]:
    if config.chunks_response_topic:
        request.set_default_response_topic(config.chunks_response_topic)
    chunks = chunk_service.create_chunks(payload)
    total_chunks = len(chunks)
    if total_chunks > config.chunks_embedding_at_once:
        request.forward_response_to_topic(config.request_embeddings_topic)
    yield from chunks


@router.post("/requests/embeddings")
@gcp_pubsub_push_handler()
def handle_push_embeddings(
    embedding_service: EmbeddingServiceDep, payload: ChunkWithEmebeddings
) -> ChunkWithEmebeddings:
    payload.embedding = embedding_service.generate_embeddings(payload.embedding_model_name, payload.text)
    return payload
