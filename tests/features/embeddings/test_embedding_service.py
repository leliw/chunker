from app.features.embeddings.embedding_service import EmbeddingService
from config import ServerConfig


def test_loading_model(config: ServerConfig):
    # Given: A model name
    model_name = "ipipan/silver-retriever-base-v1.1"
    # When: The model is loaded
    embedding_service = EmbeddingService(config)
    model = embedding_service.get_model(model_name)
    # Then: The model should be loaded successfully
    assert model_name in embedding_service.models
    assert model is not None

def test_get_models(config: ServerConfig):
    # Given: A data directory with models
    # When: The models are retrieved
    embedding_service = EmbeddingService(config)
    models = embedding_service.get_model_names()
    # Then: The models should be a list of strings
    assert isinstance(models, list)
    assert len(models) > 0
    for model in models:
        assert isinstance(model, str)
    assert len(model.split("/")) == 2  # Check if the model name is in the format "namespace/model_name"

def test_generate_embeddings(config: ServerConfig):
    # Given: A model name and some text
    model_name = "ipipan/silver-retriever-base-v1.1"
    text = "This is a test sentence."
    # When: The model is loaded and embeddings are generated
    embedding_service = EmbeddingService(config)
    embeddings = embedding_service.generate_embeddings(model_name,text)
    # Then: The embeddings should be generated successfully
    assert isinstance(embeddings, list)
    assert len(embeddings) > 0

def test_compare_embeddings(config: ServerConfig):
    # Given: A model name and two sets of text
    model_name = "ipipan/silver-retriever-base-v1.1"
    text1 = "This is a test sentence."
    text2 = "This is another test sentence."
    # When: The model is loaded and embeddings are generated
    embedding_service = EmbeddingService(config)
    embedding1 = embedding_service.generate_embeddings(model_name, text1)
    embedding2 = embedding_service.generate_embeddings(model_name, text2)
    # When: The embeddings are compared
    similarity_score = embedding_service.compare_embeddings(model_name, embedding1, embedding2)
    # Then: The similarity score should be a float
    assert isinstance(similarity_score, float)
    # And: The similarity score should be between 0 and 1
    assert 0 <= similarity_score <= 1
