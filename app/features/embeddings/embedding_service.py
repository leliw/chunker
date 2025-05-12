from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "default_model"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def get_models(self):
        """
        Return a list of available models.
        """
        return [self.model_name]

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
    
