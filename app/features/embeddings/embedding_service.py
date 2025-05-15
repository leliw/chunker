import os
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, data_dir: str = "./data", model_name: str = None, model: SentenceTransformer = None):
        self.data_dir = data_dir
        self.model_name = model_name or self.get_models()[0]
        self.model = model or SentenceTransformer(f"{data_dir}/{self.model_name}")

    def get_models(self):
        """
        Return a list of available models.
        """
        models = []
        for name1 in os.listdir(self.data_dir):
            path = os.path.join(self.data_dir, name1)
            if os.path.isdir(path):
                for name2 in os.listdir(path):
                    if os.path.isdir(os.path.join(path, name2)):
                        name = f"{name1}/{name2}"
                        models.append(name)
        return models

    def generate_embeddings(self, text) -> list[float]:
        """
        Generate embeddings for the given text using the specified model.
        """
        return self.model.encode(text, show_progress_bar = False).tolist()

    def compare_embeddings(self, embedding1, embedding2) -> float:
        """
        Compare two embeddings and return a similarity score.
        """
        return self.model.similarity(embedding1, embedding2).item()
    
