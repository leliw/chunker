from typing import List

from dependencies import ChunkServiceDep, EmbeddingServiceDep
from fastapi import APIRouter
from features.chunks.chunk_model import ChunksRequest, ChunkWithEmebeddings

router = APIRouter(tags=["Chunks"])


@router.post("/")
async def create_chunks(chunk_service: ChunkServiceDep, body: ChunksRequest) -> List[str]:
    """
    Create chunks for the given text.
    """
    return [c[0] for c in chunk_service.create_chunks(body.text)]


@router.post("/with-embeddings")
async def create_chunks_with_embeddings(
    chunk_service: ChunkServiceDep, embedding_service: EmbeddingServiceDep, chunks_request: ChunksRequest
) -> List[ChunkWithEmebeddings]:
    """
    Create chunks with embeddings for the given text.
    """
    ret = []
    chunks = chunk_service.create_chunks(chunks_request.text)
    total_chunks = len(chunks)
    for i, t in enumerate(chunks):
        ret.append(
            ChunkWithEmebeddings(
                page_id=chunks_request.job_id,
                job_id=chunks_request.job_id,
                task_id=chunks_request.task_id,
                chunk_index=i,
                total_chunks=total_chunks,
                language="pl",
                text=t[0],
                token_count=t[1],
                embedding=embedding_service.generate_embeddings(t),
                metadata=chunks_request.metadata,
            )
        )
    return ret
