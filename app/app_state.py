import logging
from dataclasses import dataclass

from config import ServerConfig
from features.embeddings.embedding_service import EmbeddingService

_log = logging.getLogger(__name__)


@dataclass
class AppState:
    config: ServerConfig
    embedding_service: EmbeddingService

    @classmethod
    def create(cls, config: ServerConfig):
        return cls(
            config=config,
            embedding_service=EmbeddingService(config),
        )
