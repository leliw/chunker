from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, model_validator


class GcpFile(BaseModel):
    bucket: Optional[str] = None
    name: str


class ChunksRequest(BaseModel):
    job_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    language: Optional[str] = None
    embedding_model_name: Optional[str] = None
    text: Optional[str] = None
    input_file: Optional[GcpFile] = None
    metadata: Optional[Dict[str, str]] = None

    @model_validator(mode="after")
    def check_text_or_input_file(self) -> "ChunksRequest":
        """
        Validates that either 'text' or 'input_file' is provided, but not both.
        """
        if self.text is not None and self.input_file is not None:
            raise ValueError("Either 'text' or 'input_file' must be provided, not both.")
        if self.text is None and self.input_file is None:
            raise ValueError("Either 'text' or 'input_file' must be provided.")
        return self


class ChunkWithEmbeddings(BaseModel):
    job_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    chunk_index: int
    total_chunks: int
    language: str
    embedding_model_name: str
    text: str
    token_count: Optional[int] = None
    embedding: List[float]
    metadata: Optional[Dict[str, str]] = None
    created_at: datetime = datetime.now(timezone.utc)
