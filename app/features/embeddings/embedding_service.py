import os
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, data_dir: str = "./data", model_name: str = "default_model"):
        self.data_dir = data_dir
        self.model_name = model_name
        self.model = SentenceTransformer(f"{data_dir}/{model_name}")

    def get_models(self):
        """
        Return a list of available models.
        """
        models = []
        for root, dirs, files in os.walk(self.data_dir):
            # Split the path to check the depth
            depth = root.count(os.sep) - self.data_dir.count(os.sep)
            if depth == 2:
                models.extend([os.path.join(root, d) for d in dirs])
            # We only need to go two levels deep, so if we are deeper than that,
            # we can clear the dirs list to prevent further traversal in this branch.
            if depth >= 2:
                dirs.clear()
        return models

    def generate_embeddings(self, text) -> list[float]:
        """
        Generate embeddings for the given text using the specified model.
        """
        return self.model.encode(text).tolist()

    def compare_embeddings(self, embedding1, embedding2) -> float:
        """
        Compare two embeddings and return a similarity score.
        """
        return self.model.similarity(embedding1, embedding2).item()
    
