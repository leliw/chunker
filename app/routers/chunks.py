from typing import Annotated, List
from dependencies import AppDep, ConfigDep, EmbeddingServiceDep
from fastapi import APIRouter, Depends
from features.chunk.chunk_service import ChunkService
from pydantic import BaseModel

router = APIRouter(tags=["Chunks"])


def get_chunk_service(app: AppDep, config: ConfigDep) -> ChunkService:
    return ChunkService(app.state.embedding_model, config.model_max_seq_length)


ChunkServiceDep = Annotated[ChunkService, Depends(get_chunk_service)]


class ChunksRequest(BaseModel):
    text: str

class ChunkWithEmmebeddings(BaseModel):
    index: int
    text: str
    embedding: list[float]

@router.post("/")
async def create_chunks(
    chunk_service: ChunkServiceDep, body: ChunksRequest
) -> list[str]:
    """
    Create chunks for the given text.
    """
    return chunk_service.create_chunks(body.text)

@router.post("/with-embeddings")
async def create_chunks_with_embeddings(
    chunk_service: ChunkServiceDep, embedding_service: EmbeddingServiceDep, body: ChunksRequest
) -> List[ChunkWithEmmebeddings]:
    """
    Create chunks with embeddings for the given text.
    """
    ret = []
    for i, t in enumerate(chunk_service.create_chunks(body.text)):
        ret.append(ChunkWithEmmebeddings(index=i, text=t, embedding=embedding_service.generate_embeddings(t)))
    return ret