from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from features.embeddings.embedding_service import EmbeddingService

router = APIRouter(tags=["Embeddings"])

def get_embedding_server() -> EmbeddingService:
    return EmbeddingService("ipipan/silver-retriever-base-v1.1")

EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_server)]

class EmbeddingRequest(BaseModel):
    text: str

@router.get("/models")
async def get_models(embdedding_service: EmbeddingServiceDep) -> list[str]:
    return embdedding_service.get_models()


@router.post("/generate")
async def generate_embeddings(embdedding_service: EmbeddingServiceDep, body: EmbeddingRequest) -> list[float]:
    """
    Generate embeddings for the given text using the specified model.
    """
    return embdedding_service.generate_embeddings(body.text)
