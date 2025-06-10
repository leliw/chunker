from dependencies import EmbeddingServiceDep
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Embeddings"])


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
