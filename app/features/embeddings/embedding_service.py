import os
from typing import Dict, List, Optional

from config import ServerConfig
from sentence_transformers import SentenceTransformer

from .embedding_model import EmbeddingPassageRequest, EmbeddingQueryRequest, EmbeddingResponse


class EmbeddingService:
    def __init__(self, config: ServerConfig):
        """Initialize the EmbeddingService.

        Args:
            data_dir (str): The directory where the models are stored.
        """
        self.data_dir = config.data_dir
        self.default_model_for_language = config.default_model_for_language
        self.models: Dict[str, Optional[SentenceTransformer]] = {}

    def get_model_names(self) -> List[str]:
        """Return a list of available models."""
        if not self.models:
            for name1 in os.listdir(self.data_dir):
                path = os.path.join(self.data_dir, name1)
                if os.path.isdir(path):
                    for name2 in os.listdir(path):
                        if os.path.isdir(os.path.join(path, name2)):
                            name = f"{name1}/{name2}"
                            self.models[name] = None
        return list(self.models.keys())  # Converted dict_keys to a list

    def get_model(self, model_name: str) -> SentenceTransformer:
        """Get a SentenceTransformer model by name.

        Args:
            model_name (str): The name of the model.

        Returns:
            SentenceTransformer: The SentenceTransformer model.
        """
        if self.models.get(model_name) is None:
            self.models[model_name] = SentenceTransformer(model_name)
        model = self.models[model_name]
        if not model:
            raise ValueError(f"Model '{model_name}' not found.")
        return model

    # @deprecated(reason="Use generate_query_embeddings or generate_passage_embedding instead")
    def generate_embeddings(self, model_name: str, text: str) -> List[float]:
        """Generate embeddings for the given text using the specified model.

        Args:
            model_name (str): The name of the model.
            text (str): The text to generate embeddings for
        Returns:
            List[float]: The generated embeddings.
        """
        model = self.get_model(model_name)
        return model.encode(text, show_progress_bar=False).tolist()

    def generate_query_embeddings(self, req: EmbeddingQueryRequest) -> EmbeddingResponse:
        """Generate embeddings for the given *question* using the specified model.

        Args:
            req (EmbeddingQueryRequest): The request object.
        Returns:
            EmbeddingResponse: The response object containing the generated embeddings.
        """
        if not req.embedding_model_name:
            req.embedding_model_name = self.find_model_name(req.language)
        model = self.get_model(req.embedding_model_name)
        match req.embedding_model_name:
            case "ipipan/silver-retriever-base-v1.1":
                # Polish Silver Retriever model expects the input question to be prefixed with "Pytanie:"
                embedding = model.encode(f"Pytanie: {req.text}", show_progress_bar=False).tolist()
                return EmbeddingResponse(embedding=embedding, language=req.language, embedding_model_name=req.embedding_model_name)
            case "Qwen/Qwen3-Embedding-0.6B":
                # Qwen model expects the input question with prompt_name
                embedding = model.encode(req.text, show_progress_bar=False, prompt_name="query").tolist()
                return EmbeddingResponse(embedding=embedding, language=req.language, embedding_model_name=req.embedding_model_name)
            case _:
                embedding = model.encode(req.text, show_progress_bar=False).tolist()
                return EmbeddingResponse(embedding=embedding, language=req.language, embedding_model_name=req.embedding_model_name)

    def generate_passage_embeddings(self, req: EmbeddingPassageRequest) -> EmbeddingResponse:
        """Generate embeddings for the given *passage* (fragment of text)using the specified model.

        Args:
            req (EmbeddingPassageRequest): The request object.
        Returns:
            EmbeddingResponse: The response object containing the generated embeddings.
        """
        if not req.embedding_model_name:
            req.embedding_model_name = self.find_model_name(req.language)
        model = self.get_model(req.embedding_model_name)
        match req.embedding_model_name:
            case "ipipan/silver-retriever-base-v1.1":
                # Polish Silver Retriever model expects the title and text with the special token "</s>"
                embedding = model.encode(f"{req.title}</s>{req.text}", show_progress_bar=False).tolist()
                return EmbeddingResponse(embedding=embedding, language=req.language, embedding_model_name=req.embedding_model_name)
            case _:
                embedding = model.encode(req.text, show_progress_bar=False).tolist()
                return EmbeddingResponse(embedding=embedding, language=req.language, embedding_model_name=req.embedding_model_name)

    def compare_embeddings(self, model_name: str, embedding1, embedding2) -> float:
        """Compare two embeddings and return a similarity score.

        Args:
            model_name (str): The name of the model.
            embedding1 (List[float]): The first embedding.
            embedding2 (List[float]): The second embedding.
        Returns:
            float: The similarity score.
        """
        model = self.get_model(model_name)
        return model.similarity(embedding1, embedding2).item()

    def find_model_name(self, language: str) -> str:
        """Find the best model for the given language.

        Args:
            language (str): The language.
        Returns:
            str: The name of the best model.
        """
        return self.default_model_for_language.get(language, "ipipan/silver-retriever-base-v1.1")
