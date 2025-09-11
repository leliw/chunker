import logging
from typing import Dict, Iterator, Optional

from ampf.gcp import GcpPubsubRequest, gcp_pubsub_push_handler
from dependencies import ChunkServiceDep, ConfigDep, EmbeddingServiceDep
from fastapi import APIRouter
from log_context import job_id_context, task_id_context
from pydantic import BaseModel
from routers.chunks import ChunksRequest, ChunkWithEmbeddings

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
    request: GcpPubsubRequest,
    payload: ChunksRequest,
) -> Iterator[ChunkWithEmbeddings]:
    # Set context variables for logging.
    job_id_context.set(payload.job_id)
    task_id_context.set(payload.task_id)
    if config.chunks_response_topic:
        request.set_default_response_topic(config.chunks_response_topic)
    _log.debug("Start processing chunks, job=%s, task=%s", payload.job_id, payload.task_id)
    chunks = chunk_service.create_chunks(payload)
    total_chunks = len(chunks)
    _log.debug("Total chunks: %s, job=%s, task=%s", total_chunks, payload.job_id, payload.task_id)
    if total_chunks > config.chunks_embedding_at_once:
        request.forward_response_to_topic(config.request_embeddings_topic)
    yield from chunks
    _log.debug("End processing chunks, job=%s, task=%s", payload.job_id, payload.task_id)



@router.post("/requests/embeddings")
@gcp_pubsub_push_handler()
def handle_push_embeddings(
    embedding_service: EmbeddingServiceDep, payload: ChunkWithEmbeddings
) -> ChunkWithEmbeddings:
    # Set context variables for logging.
    job_id_context.set(payload.job_id)
    task_id_context.set(payload.task_id)
    payload.embedding = embedding_service.generate_embeddings(payload.embedding_model_name, payload.text)
    return payload
