from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from dependencies import ChunkServiceDep, EmbeddingServiceDep
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["Chunks"])


class ChunksRequest(BaseModel):
    page_id: UUID
    task_id: Optional[UUID] = None
    text: str


class ChunkWithEmmebeddings(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    page_id: UUID
    task_id: Optional[UUID] = None
    chunk_index: int
    language: str
    text: str
    token_count: Optional[int] = None
    embedding: List[float]
    created_at: datetime = datetime.now(timezone.utc)


@router.post("/")
async def create_chunks(chunk_service: ChunkServiceDep, body: ChunksRequest) -> List[str]:
    """
    Create chunks for the given text.
    """
    return [c[0] for c in chunk_service.create_chunks(body.text)]


@router.post("/with-embeddings")
async def create_chunks_with_embeddings(
    chunk_service: ChunkServiceDep, embedding_service: EmbeddingServiceDep, chunks_request: ChunksRequest
) -> List[ChunkWithEmmebeddings]:
    """
    Create chunks with embeddings for the given text.
    """
    ret = []
    for i, t in enumerate(chunk_service.create_chunks(chunks_request.text)):
        ret.append(
            ChunkWithEmmebeddings(
                page_id=chunks_request.page_id,
                task_id=chunks_request.task_id,
                chunk_index=i,
                text=t[0],
                token_count=t[1],
                language='pl',
                embedding=embedding_service.generate_embeddings(t),
            )
        )
    return ret
