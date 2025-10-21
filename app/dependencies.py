import logging
from typing import Annotated, Optional

from config import ServerConfig
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from features.chunks.chunk_service import ChunkService
from features.embeddings.embedding_service import EmbeddingService

load_dotenv()

_log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = ServerConfig()
    _log.info("Version: %s", config.version)
    app.state.config = config
    app.state.embedding_service = EmbeddingService(config)
    yield


def get_app(request: Request) -> FastAPI:
    return request.app


AppDep = Annotated[FastAPI, Depends(get_app)]


def get_server_config(app: AppDep) -> ServerConfig:
    return app.state.config


ConfigDep = Annotated[ServerConfig, Depends(get_server_config)]


async def verify_api_key(
    config: ConfigDep,
    x_api_key: Annotated[Optional[str], Header(description="Required for authentication")] = None,
):
    if config.api_key:
        if not x_api_key:
            _log.warning("Missing API key")
            raise HTTPException(status_code=403, detail="Missing API key")
        if x_api_key != config.api_key:
            _log.warning("Invalid API key")
            raise HTTPException(status_code=403, detail="Invalid API key")
        _log.debug("API key verified")
    else:
        _log.debug("API key not required")


def get_embedding_service(app: AppDep) -> EmbeddingService:
    return app.state.embedding_service


EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]


def get_chunk_service(config: ConfigDep, embedding_service: EmbeddingServiceDep) -> ChunkService:
    # Pass the dictionary of models to the ChunkService
    return ChunkService(embedding_service, config.chunks_embedding_at_once)


ChunkServiceDep = Annotated[ChunkService, Depends(get_chunk_service)]
