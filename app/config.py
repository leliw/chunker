from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = "0.1.1"
    data_dir: str = "./data"
    model_name: Optional[str] = None
    api_key: Optional[str] = None

class ClientConfig(BaseModel):
    version: str