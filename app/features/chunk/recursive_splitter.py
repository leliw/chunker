from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


class RecursiveSplitter:
    """
    Splits text into chunks recursively based on character count and embedding model tokens.
    """

    def __init__(self, model: SentenceTransformer, chunk_size: int, chunk_overlap: int = 128):
        self.model = model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[Document]:
        """
        Split the given text into chunks recursively.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.count_tokens,
            is_separator_regex=False,
        )
        chunks = text_splitter.create_documents([text])
        return chunks or [Document(page_content="")]

    def count_tokens(self, text: str) -> int:
        """
        Returns the number of tokens in the given text according to the SentenceTransformer model.
        """
        # Tokenize the input text and count the number of token IDs
        return len(self.model.tokenize([text])["input_ids"].tolist()[0])
