import logging
from dataclasses import dataclass

from ampf.base import BaseAsyncFactory
from app_config import AppConfig
from ampf.gcp import GcpAsyncFactory
from features.embeddings.embedding_service import EmbeddingService

_log = logging.getLogger(__name__)


@dataclass
class AppState:
    config: AppConfig
    async_factory: BaseAsyncFactory
    embedding_service: EmbeddingService

    @classmethod
    def create(cls, config: AppConfig):
        return cls(
            config=config,
            async_factory=GcpAsyncFactory(),
            embedding_service=EmbeddingService(config),
        )
