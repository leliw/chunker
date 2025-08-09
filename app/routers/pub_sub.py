import base64
import logging
from typing import Dict, Optional

from ampf.gcp import GcpTopic
from dependencies import ChunkServiceDep, ConfigDep, EmbeddingServiceDep
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError
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
async def handle_push(
    config: ConfigDep, chunk_service: ChunkServiceDep, embedding_service: EmbeddingServiceDep, request: PushRequest
):
    try:
        encoded_data = request.message.data
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        if request.message.attributes:
            response_topic_name = request.message.attributes.get("response_topic")
            sender_id = request.message.attributes.get("sender_id")
        else:
            response_topic_name = None
            sender_id = None
        if not response_topic_name and config.chunks_response_topic:
            response_topic_name = config.chunks_response_topic

        _log.info("Received: %s ID: %s", request.subscription, request.message.messageId)
        _log.debug("Data: %s", decoded_data)

        chunks_request = ChunksRequest.model_validate_json(decoded_data)
        chunks = chunk_service.create_chunks(chunks_request.text)
        total_chunks = len(chunks)
        for i, t in enumerate(chunks):
            ret = ChunkWithEmmebeddings(
                page_id=chunks_request.page_id,
                job_id=chunks_request.job_id,
                task_id=chunks_request.task_id,
                chunk_index=i,
                total_chunks=total_chunks,
                language="pl",
                text=t[0],
                token_count=t[1],
                embedding=embedding_service.generate_embeddings(t[0]),
                metadata=chunks_request.metadata,
            )
            if response_topic_name:
                topic = GcpTopic[ChunkWithEmmebeddings](response_topic_name)
                topic.publish(ret, {"sender_id": sender_id} if sender_id else None)

        return {"status": "acknowledged", "messageId": request.message.messageId}
    except ValidationError as e:
        _log.error("Error processing message ID: %s: %s", request.message.messageId, e)
        raise HTTPException(status_code=400, detail=f"Wrong message format: {e}")

    except Exception as e:
        _log.error("Error processing message ID: %s: %s", request.message.messageId, e)
        raise HTTPException(status_code=500, detail=f"Error processing message: {e}")
