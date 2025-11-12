import logging
from typing import override

from ampf.base import BaseAsyncFactory
from ampf.gcp import GcpPubsubRequest, SubscriptionProcessor
from app_config import AppConfig
from features.chunks.chunk_model import ChunksRequest
from features.chunks.chunk_service import ChunkService
from log_context import job_id_context, task_id_context
from opentelemetry import trace

_log = logging.getLogger(__name__)
_tracer = trace.get_tracer(__name__)


class ChunkRequestMessageRouter(SubscriptionProcessor[ChunksRequest]):
    """Router for processing chunk requests from a Pub/Sub subscription.

    This class extends `SubscriptionProcessor` to handle `ChunksRequest` messages.
    It processes incoming chunking requests, creates chunks using `ChunkService`,
    and publishes the results to a Pub/Sub topic.
    """

    def __init__(
        self,
        config: AppConfig,
        async_factory: BaseAsyncFactory,
        chunk_service: ChunkService,
    ):
        super().__init__(async_factory, ChunksRequest)
        self.chunks_response_topic = config.chunking_responses_topic
        self.chunk_embedding_requests_topic = config.chunk_embedding_requests_topic
        self.chunks_embedding_at_once = config.chunks_embedding_at_once
        self.chunk_service = chunk_service

    @override
    async def process_request(self, request: GcpPubsubRequest) -> None:
        payload = request.decoded_data(self.clazz)
        try:
            with _tracer.start_as_current_span("requests") as span:
                # Set context variables for logging.
                job_id_context.set(payload.job_id)
                task_id_context.set(payload.task_id)
                span.set_attribute("job_id", str(payload.job_id))
                span.set_attribute("task_id", str(payload.task_id))

                if self.chunks_response_topic:
                    request.set_default_response_topic(self.chunks_response_topic)
                _log.debug(
                    "Start processing chunks, job=%s, task=%s",
                    payload.job_id,
                    payload.task_id,
                    extra={"metadata": payload.metadata},
                )
                chunks = self.chunk_service.create_chunks(payload)
                total_chunks = len(chunks)
                span.set_attribute("total_chunks", total_chunks)
                _log.debug("Total chunks: %s, job=%s, task=%s", total_chunks, payload.job_id, payload.task_id)
                if total_chunks > self.chunks_embedding_at_once:
                    request.forward_response_to_topic(self.chunk_embedding_requests_topic)
                for chunk in chunks:
                    await self.process_response(request, chunk)
                _log.debug(
                    "End processing chunks, job=%s, task=%s",
                    payload.job_id,
                    payload.task_id,
                    extra={"metadata": payload.metadata},
                )
        except Exception as e:
            _log.warning("Failed to process message ID:%s", request.message.messageId)
            _log.exception(e)
            raise e
