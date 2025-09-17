import logging
from typing import List

from features.chunks.chunk_model import ChunksRequest, ChunkWithEmbeddings
from features.embeddings.embedding_model import EmbeddingPassageRequest
from features.embeddings.embedding_service import EmbeddingService

from .recursive_splitter import RecursiveSplitter


class ChunkService:
    """Service for creating chunks from text using different embedding models."""
    _log = logging.getLogger(__name__)

    def __init__(
        self, embedding_service: EmbeddingService, chunks_embedding_at_once: int = 4, chunk_overlap: int = 128
    ):
        """
        Initializes the ChunkService.

        Args:
            embedding_service (EmbeddingService): The embedding service to use for chunking.
            chunk_overlap (int): The number of tokens to overlap between chunks.
        """
        self.embedding_service = embedding_service
        self.chunks_embedding_at_once = chunks_embedding_at_once
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, req: ChunksRequest, generate_embeddings: bool | None = None) -> List[ChunkWithEmbeddings]:
        """
        Create chunks for the given text using a specified model.

        Args:
            req (ChunksRequest): The request object containing the text to chunk.

        Returns:
            List[ChunkWithEmebeddings]: A list of chunks with embeddings.

        Raises:
            ValueError: If the specified model_name is not available.
        """
        if req.input_file:
            from ampf.gcp import GcpFactory

            factory = GcpFactory(bucket_name=req.input_file.bucket)
            bs = factory.create_blob_storage("", content_type="text/markdown")
            file_content = bs.download_blob(req.input_file.name)
            text = file_content.decode("utf-8")
        elif req.text:
            text = req.text
        else:
            raise ValueError("Either 'text' or 'input_file' must be provided.")

        if not req.language:
            req.language = self.embedding_service.detect_language(text)
        if not req.embedding_model_name:
            req.embedding_model_name = self.embedding_service.find_model_name(req.language)
        model = self.embedding_service.get_model(req.embedding_model_name)
        self._log.info("Start splitting.")
        splitter = RecursiveSplitter(model=model, chunk_size=model.max_seq_length, chunk_overlap=self.chunk_overlap)
        chunks = splitter.split(text)
        self._log.info("End splitting.")
        total_chunks = len(chunks)
        self._log.info("Total chunks: %s", total_chunks)
        if generate_embeddings is None:
            generate_embeddings = total_chunks <= self.chunks_embedding_at_once
        if generate_embeddings:
            self._log.info("Start generating embeddings.")
        ret = []
        for i, doc in enumerate(chunks):
            if generate_embeddings:
                e_req = EmbeddingPassageRequest(
                    language=req.language,
                    embedding_model_name=req.embedding_model_name,
                    text=doc.page_content,
                    title=doc.metadata.get("title"),
                )
                embedding = self.embedding_service.generate_passage_embeddings(e_req).embedding
            else:
                embedding = []
            ret.append(
                ChunkWithEmbeddings(
                    job_id=req.job_id,
                    task_id=req.task_id,
                    chunk_index=i,
                    total_chunks=total_chunks,
                    language=req.language,
                    embedding_model_name=req.embedding_model_name,
                    text=doc.page_content,
                    token_count=splitter.count_tokens(doc.page_content),
                    embedding=embedding,
                    metadata=req.metadata,
                )
            )
            self._log.info("Chunk %s/%s generated.", i + 1, total_chunks)
        self._log.info("End chunking.")
        return ret
