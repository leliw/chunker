import os
from typing import Dict, List, Optional

from sentence_transformers import SentenceTransformer

from config import ServerConfig


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
        return list(self.models.keys()) # Converted dict_keys to a list

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

    def generate_query_embeddings(self, model_name:str, text: str) -> List[float]:
        """Generate embeddings for the given *question* using the specified model.

        Args:
            model_name (str): The name of the model.
            text (str): The question to generate embeddings for
        Returns:
            List[float]: The generated embeddings.
        """
        if "silver-retriever" in model_name and not text.startswith("Pytanie:"):
            # Polish Silver Retriever model expects the input question to be prefixed with "Pytanie:"
            return self.generate_embeddings(model_name, f"Pytanie: {text}")
        else:
            return self.generate_embeddings(model_name, text)

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

    def find_model(self, language: str) -> str:
        """Find the best model for the given language.

        Args:
            language (str): The language.
        Returns:
            str: The name of the best model.
        """
        return self.default_model_for_language.get(language, "ipipan/silver-retriever-base-v1.1")