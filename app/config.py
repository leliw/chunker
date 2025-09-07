from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from version import __version__


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = __version__
    data_dir: str = "./data"
    model_names: list[str] = []
    api_key: Optional[str] = None

    chunks_response_topic: Optional[str] = None
    chunks_embedding_at_once: int = 4
    request_embeddings_topic: str = "chunker-embeddings-requests"


class ClientConfig(BaseModel):
    version: str
