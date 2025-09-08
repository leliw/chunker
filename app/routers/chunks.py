from typing import List

from dependencies import ChunkServiceDep, EmbeddingServiceDep
from fastapi import APIRouter
from features.chunks.chunk_model import ChunksRequest, ChunkWithEmebeddings

router = APIRouter(tags=["Chunks"])


@router.post("/")
async def create_chunks(chunk_service: ChunkServiceDep, chunks_request: ChunksRequest) -> List[str]:
    """
    Create chunks for the given text.
    """
    return [c.text for c in chunk_service.create_chunks(chunks_request, generate_embeddings=False)]


@router.post("/with-embeddings")
async def create_chunks_with_embeddings(
    chunk_service: ChunkServiceDep, embedding_service: EmbeddingServiceDep, chunks_request: ChunksRequest
) -> List[ChunkWithEmebeddings]:
    """
    Create chunks with embeddings for the given text.
    """
    return chunk_service.create_chunks(chunks_request, generate_embeddings=False)
