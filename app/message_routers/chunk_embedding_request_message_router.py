import logging
from typing import override

from ampf.base import BaseAsyncFactory
from ampf.gcp import SubscriptionProcessor
from features.chunks.chunk_model import ChunkWithEmbeddings
from features.embeddings.embedding_service import EmbeddingService
from log_context import job_id_context, task_id_context
from opentelemetry import trace

_log = logging.getLogger(__name__)
_tracer = trace.get_tracer(__name__)


class ChunkEmbeddingRequestMessageRouter(SubscriptionProcessor[ChunkWithEmbeddings]):
    """Router for processing chunk embedding calculations requests from a Pub/Sub subscription."""
    def __init__(
        self,
        async_factory: BaseAsyncFactory,
        embedding_service: EmbeddingService,
    ):
        super().__init__(async_factory, ChunkWithEmbeddings)
        self.embedding_service = embedding_service

    @override
    async def process_payload(self, payload: ChunkWithEmbeddings) -> ChunkWithEmbeddings:
        with _tracer.start_as_current_span("requests") as span:
            # Set context variables for logging.
            job_id_context.set(payload.job_id)
            task_id_context.set(payload.task_id)
            span.set_attribute("job_id", str(payload.job_id))
            span.set_attribute("task_id", str(payload.task_id))
            payload.embedding = self.embedding_service.generate_embeddings(payload.embedding_model_name, payload.text)
            _log.debug(
                "Embeddings generated, job=%s, task=%s",
                payload.job_id,
                payload.task_id,
                extra={"metadata": payload.metadata},
            )
            return payload