from typing import List, Tuple

from features.embeddings.embedding_service import EmbeddingService

from .recursive_splitter import RecursiveSplitter


class ChunkService:
    """Service for creating chunks from text using different embedding models."""

    def __init__(self, embedding_service: EmbeddingService, chunk_overlap: int = 128):
        """
        Initializes the ChunkService.

        Args:
            embedding_service (EmbeddingService): The embedding service to use for chunking.
            chunk_overlap (int): The number of tokens to overlap between chunks.
        """
        self.embedding_service = embedding_service
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, model_name: str, text: str) -> List[Tuple[str, int]]:
        """
        Create chunks for the given text using a specified model.

        Args:
            model_name (str): The name of the model to use for chunking and token counting.
            text (str): The input text to be chunked.

        Returns:
            List[Tuple[str, int]]: A list of tuples, where each tuple contains the chunk text and its token count.

        Raises:
            ValueError: If the specified model_name is not available.
        """
        model = self.embedding_service.get_model(model_name)
        splitter = RecursiveSplitter(model=model, chunk_size=model.max_seq_length, chunk_overlap=self.chunk_overlap)
        chunks = splitter.split(text)
        return [(chunk.page_content, splitter.count_tokens(chunk.page_content)) for chunk in chunks]
