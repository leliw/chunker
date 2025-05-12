import logging
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.concurrency import asynccontextmanager

from config import ServerConfig

load_dotenv()

_log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = ServerConfig()
    app.state.config = config
    yield


def get_app(request: Request) -> FastAPI:
    return request.app


AppDep = Annotated[FastAPI, Depends(get_app)]


def get_server_config(app: AppDep) -> ServerConfig:
    return app.state.config


ConfigDep = Annotated[ServerConfig, Depends(get_server_config)]
