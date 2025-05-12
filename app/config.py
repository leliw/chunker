from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = "0.0.1"
    data_dir: str = "./data"
    model_name: str = "ipipan/silver-retriever-base-v1.1"

class ClientConfig(BaseModel):
    version: str