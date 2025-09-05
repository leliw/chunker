
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class GcpFile(BaseModel):
    bucket: Optional[str] = None
    name: str


class ChunksRequest(BaseModel):
    page_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    text: str
    metadata: Optional[Dict[str, str]] = None


class ChunkWithEmebeddings(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    page_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    chunk_index: int
    total_chunks: int
    language: str
    text: str
    token_count: Optional[int] = None
    embedding: List[float]
    metadata: Optional[Dict[str, str]] = None
    created_at: datetime = datetime.now(timezone.utc)
