import logging
from typing import Iterator

from ampf.gcp import GcpPubsubRequest, gcp_pubsub_push_handler
from dependencies import ChunkServiceDep, ConfigDep, EmbeddingServiceDep
from fastapi import APIRouter
from log_context import job_id_context, task_id_context
from routers.chunks import ChunksRequest, ChunkWithEmbeddings
from opentelemetry import trace

_log = logging.getLogger(__name__)

router = APIRouter(tags=["Pub/Sub Push"])

tracer = trace.get_tracer("pub-sub.tracer")

@router.post("/requests")
@gcp_pubsub_push_handler()
def handle_push(
    config: ConfigDep,
    chunk_service: ChunkServiceDep,
    request: GcpPubsubRequest,
    payload: ChunksRequest,
) -> Iterator[ChunkWithEmbeddings]:
    with tracer.start_as_current_span("requests") as requestsspan:
        # Set context variables for logging.
        job_id_context.set(payload.job_id)
        task_id_context.set(payload.task_id)
        requestsspan.set_attribute("job_id", str(payload.job_id))
        requestsspan.set_attribute("task_id", str(payload.task_id))

        if config.chunks_response_topic:
            request.set_default_response_topic(config.chunks_response_topic)
        _log.debug("Start processing chunks, job=%s, task=%s", payload.job_id, payload.task_id, extra={"metadata": payload.metadata})
        chunks = chunk_service.create_chunks(payload)
        total_chunks = len(chunks)
        requestsspan.set_attribute("total_chunks",total_chunks)
        _log.debug("Total chunks: %s, job=%s, task=%s", total_chunks, payload.job_id, payload.task_id)
        if total_chunks > config.chunks_embedding_at_once:
            request.forward_response_to_topic(config.request_embeddings_topic)
        yield from chunks
        _log.debug("End processing chunks, job=%s, task=%s", payload.job_id, payload.task_id, extra={"metadata": payload.metadata})


@router.post("/requests/embeddings")
@gcp_pubsub_push_handler()
def handle_push_embeddings(embedding_service: EmbeddingServiceDep, payload: ChunkWithEmbeddings) -> ChunkWithEmbeddings:
    with tracer.start_as_current_span("requests") as requestsspan:
        # Set context variables for logging.
        job_id_context.set(payload.job_id)
        task_id_context.set(payload.task_id)
        requestsspan.set_attribute("job_id", str(payload.job_id))
        requestsspan.set_attribute("task_id", str(payload.task_id))
        payload.embedding = embedding_service.generate_embeddings(payload.embedding_model_name, payload.text)
        _log.debug("Embeddings generated, job=%s, task=%s", payload.job_id, payload.task_id, extra={"metadata": payload.metadata})
        return payload
