from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from version import __version__


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = __version__

    data_dir: str = "./data"
    default_model_for_language: Dict[str, str] = {"pl": "ipipan/silver-retriever-base-v1.1", "en": "Qwen/Qwen3-Embedding-0.6B"}
    api_key: Optional[str] = None

    chunks_embedding_at_once: int = 4
    
    chunking_requests_topic: Optional[str] = None
    chunking_responses_topic: Optional[str] = None
    chunk_embedding_requests_topic: str = "chunker-embeddings-requests"

    @property
    def model_names(self) -> List[str]:
        return list(self.default_model_for_language.values())


class ClientConfig(BaseModel):
    version: str
