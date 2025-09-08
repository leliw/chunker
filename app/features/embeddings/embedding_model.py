from typing import List, Optional

from pydantic import BaseModel


class EmbeddingQueryRequest(BaseModel):
    language: Optional[str] = None
    embedding_model_name: Optional[str] = None
    text: str

class EmbeddingPassageRequest(BaseModel):
    language: Optional[str] = None
    embedding_model_name: Optional[str] = None
    title: Optional[str] = None
    text: str

class EmbeddingResponse(BaseModel):
    language: str
    embedding_model_name: str
    embedding: List[float]
