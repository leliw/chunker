from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dependencies import AppDep, ConfigDep
from features.embeddings.embedding_service import EmbeddingService

router = APIRouter(tags=["Embeddings"])


class EmbeddingRequest(BaseModel):
    text: str


def get_embedding_server(app: AppDep, config: ConfigDep) -> EmbeddingService:
    return EmbeddingService(
        config.data_dir, config.model_name, app.state.embedding_model
    )


EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_server)]


@router.get("/models")
async def get_models(embdedding_service: EmbeddingServiceDep) -> list[str]:
    return embdedding_service.get_models()


@router.post("/generate")
async def generate_embeddings(
    embdedding_service: EmbeddingServiceDep, body: EmbeddingRequest
) -> list[float]:
    """
    Generate embeddings for the given text using the specified model.
    """
    return embdedding_service.generate_embeddings(body.text)
