from typing import List

from dependencies import EmbeddingServiceDep
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Embeddings"])


class EmbeddingRequest(BaseModel):
    language: str = "pl"
    embedding_model_name: str = "ipipan/silver-retriever-base-v1.1"
    text: str


class EmbeddingResponse(BaseModel):
    language: str = "pl"
    embedding_model_name: str = "ipipan/silver-retriever-base-v1.1"
    embedding: List[float]


@router.get("/models")
async def get_models(embdedding_service: EmbeddingServiceDep) -> List[str]:
    return embdedding_service.get_models()


@router.post("/generate")
async def generate_embeddings(embdedding_service: EmbeddingServiceDep, body: EmbeddingRequest) -> List[float]:
    """
    Generate embeddings for the given text using the specified model.
    """
    return embdedding_service.generate_embeddings(body.text)


@router.post("/generate/query")
async def generate_query_embeddings(
    embdedding_service: EmbeddingServiceDep, body: EmbeddingRequest
) -> EmbeddingResponse:
    """
    Generate embeddings for the given query using the specified model.
    """
    return EmbeddingResponse(embedding=embdedding_service.generate_query_embeddings(body.text))
