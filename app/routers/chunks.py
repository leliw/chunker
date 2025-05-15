from typing import Annotated
from dependencies import AppDep, ConfigDep
from fastapi import APIRouter, Depends
from features.chunk.chunk_service import ChunkService
from pydantic import BaseModel

router = APIRouter(tags=["Chunks"])


def get_chunk_service(app: AppDep, config: ConfigDep) -> ChunkService:
    return ChunkService(app.state.embedding_model, config.model_max_seq_length)


ChunkServiceDep = Annotated[ChunkService, Depends(get_chunk_service)]


class ChunksRequest(BaseModel):
    text: str


@router.post("/")
async def create_chunks(
    chunk_service: ChunkServiceDep, body: ChunksRequest
) -> list[str]:
    """
    Create chunks for the given text.
    """
    return chunk_service.create_chunks(body.text)
