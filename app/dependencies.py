import logging
from typing import Annotated, Optional

from config import ServerConfig
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from sentence_transformers import SentenceTransformer

load_dotenv()

_log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = ServerConfig()
    embedding_model = SentenceTransformer(f"{config.data_dir}/{config.model_name}")
    app.state.config = config
    app.state.embedding_model = embedding_model
    yield


def get_app(request: Request) -> FastAPI:
    return request.app


AppDep = Annotated[FastAPI, Depends(get_app)]


def get_server_config(app: AppDep) -> ServerConfig:
    return app.state.config


ConfigDep = Annotated[ServerConfig, Depends(get_server_config)]


async def verify_api_key(
    config: ConfigDep,
    x_api_key: Annotated[
        Optional[str], Header(description="Required for authentication")
    ] = None,
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
        _log.warning("API key not required")
