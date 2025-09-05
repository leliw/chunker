import logging
from typing import AsyncIterator, Dict, Optional

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
async def handle_push(
    config: ConfigDep,
    chunk_service: ChunkServiceDep,
    embedding_service: EmbeddingServiceDep,
    request: GcpPubsubRequest,
    payload: ChunksRequest,
) -> AsyncIterator[ChunkWithEmebeddings]:
    if config.chunks_response_topic:
        request.set_default_response_topic(config.chunks_response_topic)
    chunks = chunk_service.create_chunks(payload.text)
    total_chunks = len(chunks)
    if total_chunks > config.chunks_embedding_at_once:
        request.forward_response_to_topic(config.request_embeddings_topic)
        generate_embedding = False
    else:
        generate_embedding = True
    for i, t in enumerate(chunks):
        ret = ChunkWithEmebeddings(
            page_id=payload.job_id,
            job_id=payload.job_id,
            task_id=payload.task_id,
            chunk_index=i,
            total_chunks=total_chunks,
            language="pl",
            text=t[0],
            token_count=t[1],
            embedding=embedding_service.generate_embeddings(t[0]) if generate_embedding else [],
            metadata=payload.metadata,
        )
        yield ret


@router.post("/requests/embeddings")
@gcp_pubsub_push_handler()
async def handle_push_embeddings(
    embedding_service: EmbeddingServiceDep, payload: ChunkWithEmebeddings
) -> ChunkWithEmebeddings:
    payload.embedding = embedding_service.generate_embeddings(payload.text)
    return payload
