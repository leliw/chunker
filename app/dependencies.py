import logging
from typing import Annotated, Optional

from app_config import AppConfig
from app_state import AppState
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from features.chunks.chunk_service import ChunkService
from features.embeddings.embedding_service import EmbeddingService
from message_routers.chunk_request_message_router import ChunkRequestMessageRouter

load_dotenv()

_log = logging.getLogger(__name__)


def lifespan(config: AppConfig = AppConfig()):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _log.info("Version: %s", config.version)
        app_state = AppState.create(config)
        app.state.app_state = app_state

        yield

    return lifespan


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state


AppStateDep = Annotated[AppState, Depends(get_app_state)]


def get_server_config(app_state: AppStateDep) -> AppConfig:
    return app_state.config


ConfigDep = Annotated[AppConfig, Depends(get_server_config)]


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


def get_embedding_service(app_state: AppStateDep) -> EmbeddingService:
    return app_state.embedding_service


EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]


def get_chunk_service(app_state: AppStateDep) -> ChunkService:
    return ChunkService(app_state.embedding_service, app_state.config.chunks_embedding_at_once)


ChunkServiceDep = Annotated[ChunkService, Depends(get_chunk_service)]


def get_chunnk_request_message_router(app_state: AppStateDep) -> ChunkRequestMessageRouter:
    return ChunkRequestMessageRouter(
        app_state.config,
        app_state.async_factory,
        get_chunk_service(app_state),
    )


ChunkRequestMessageRouterDep = Annotated[ChunkRequestMessageRouter, Depends(get_chunnk_request_message_router)]
