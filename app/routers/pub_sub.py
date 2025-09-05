import logging
from typing import Dict, Optional

from ampf.gcp import GcpPubsubRequest, GcpTopic, gcp_pubsub_push_handler
from dependencies import ChunkServiceDep, ConfigDep, EmbeddingServiceDep
from fastapi import APIRouter
from pydantic import BaseModel
from routers.chunks import ChunksRequest, ChunkWithEmmebeddings

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
) -> None:
    if request.message.attributes:
        response_topic_name = request.message.attributes.get("response_topic")
        sender_id = request.message.attributes.get("sender_id")
    else:
        response_topic_name = None
        sender_id = None
    if not response_topic_name and config.chunks_response_topic:
        response_topic_name = config.chunks_response_topic

    _log.info("Received: %s ID: %s", request.subscription, request.message.messageId)

    chunks = chunk_service.create_chunks(payload.text)
    total_chunks = len(chunks)
    for i, t in enumerate(chunks):
        ret = ChunkWithEmmebeddings(
            page_id=payload.page_id,
            job_id=payload.job_id,
            task_id=payload.task_id,
            chunk_index=i,
            total_chunks=total_chunks,
            language="pl",
            text=t[0],
            token_count=t[1],
            embedding=embedding_service.generate_embeddings(t[0]),
            metadata=payload.metadata,
        )
        if response_topic_name:
            topic = GcpTopic[ChunkWithEmmebeddings](response_topic_name)
            topic.publish(ret, {"sender_id": sender_id} if sender_id else None)
