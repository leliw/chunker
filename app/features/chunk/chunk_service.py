from sentence_transformers import SentenceTransformer

from .recursive_splitter import RecursiveSplitter


class ChunkService:
    """    Service for creating chunks from text.
    """
    def __init__(
        self, model: SentenceTransformer, chunk_size: int, chunk_overlap: int = 128
    ):
        self.splitter = RecursiveSplitter(
            model=model, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def create_chunks(self, text: str) -> list[str]:
        """
        Create chunks for the given text.
        """
        chunks = self.splitter.split(text)
        return [chunk.page_content for chunk in chunks]
