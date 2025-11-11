import logging
from dataclasses import dataclass

from app_config import AppConfig
from features.embeddings.embedding_service import EmbeddingService

_log = logging.getLogger(__name__)


@dataclass
class AppState:
    config: AppConfig
    embedding_service: EmbeddingService

    @classmethod
    def create(cls, config: AppConfig):
        return cls(
            config=config,
            embedding_service=EmbeddingService(config),
        )
