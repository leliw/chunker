import os
import tomllib
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_version_from_pyproject():
    pyproject_path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    if not os.path.exists(pyproject_path):
        pyproject_path = os.path.join(os.path.dirname(__file__), "pyproject.toml")
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = get_version_from_pyproject()
    data_dir: str = "./data"
    model_name: str = ""
    model_max_seq_length: int = 512
    api_key: Optional[str] = None

    chunks_response_topic: Optional[str] = None
    chunks_embedding_at_once: int = 4
    request_embeddings_topic: str = "chunker-embeddings-requests"


class ClientConfig(BaseModel):
    version: str

if __name__ == "__main__":
    config = ServerConfig()
    print(config.version)