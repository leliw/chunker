import logging

from ampf.gcp import GcpPubsubRequest, GcpPubsubResponse, gcp_pubsub_process_push, gcp_pubsub_push_handler
from dependencies import ChunkRequestMessageRouterDep, EmbeddingServiceDep
from fastapi import APIRouter
from log_context import job_id_context, task_id_context
from opentelemetry import trace
from routers.chunks import ChunkWithEmbeddings

router = APIRouter(tags=["Pub/Sub Push"])

_log = logging.getLogger(__name__)
_tracer = trace.get_tracer("pub-sub.tracer")


@router.post("/requests")
async def handle_push(
    processor: ChunkRequestMessageRouterDep,
    request: GcpPubsubRequest,
) -> GcpPubsubResponse:
    return await gcp_pubsub_process_push(processor, request)


@router.post("/requests/embeddings")
@gcp_pubsub_push_handler()
def handle_push_embeddings(embedding_service: EmbeddingServiceDep, payload: ChunkWithEmbeddings) -> ChunkWithEmbeddings:
    with _tracer.start_as_current_span("requests") as span:
        # Set context variables for logging.
        job_id_context.set(payload.job_id)
        task_id_context.set(payload.task_id)
        span.set_attribute("job_id", str(payload.job_id))
        span.set_attribute("task_id", str(payload.task_id))
        payload.embedding = embedding_service.generate_embeddings(payload.embedding_model_name, payload.text)
        _log.debug(
            "Embeddings generated, job=%s, task=%s",
            payload.job_id,
            payload.task_id,
            extra={"metadata": payload.metadata},
        )
        return payload
