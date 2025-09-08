from typing import List, Optional

from dependencies import ConfigDep, EmbeddingServiceDep
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Embeddings"])


class EmbeddingRequest(BaseModel):
    language: str = "pl"
    embedding_model_name: Optional[str] = None
    text: str


class EmbeddingResponse(BaseModel):
    language: str
    embedding_model_name: str
    embedding: List[float]


@router.get("/models")
async def get_models(embdedding_service: EmbeddingServiceDep) -> List[str]:
    return embdedding_service.get_model_names()


@router.post("/generate")
async def generate_embeddings(config: ConfigDep, embdedding_service: EmbeddingServiceDep, body: EmbeddingRequest) -> List[float]:
    """
    Generate embeddings for the given text using the specified model.
    """
    if not body.embedding_model_name:
        body.embedding_model_name = embdedding_service.find_model(body.language)
    return embdedding_service.generate_embeddings(body.embedding_model_name, body.text)


@router.post("/generate/query")
def generate_query_embeddings(
    config: ConfigDep, embdedding_service: EmbeddingServiceDep, body: EmbeddingRequest
) -> EmbeddingResponse:
    """
    Generate embeddings for the given query using the specified model.
    """
    if not body.embedding_model_name:
        body.embedding_model_name = embdedding_service.find_model(body.language)
    embedding = embdedding_service.generate_query_embeddings(body.embedding_model_name, body.text)
    return EmbeddingResponse(embedding=embedding, language=body.language, embedding_model_name=body.embedding_model_name)
