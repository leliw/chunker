import os

from config import ServerConfig
from sentence_transformers import SentenceTransformer


def main():
    config = ServerConfig()
    model_name = config.model_name
    local_save_directory = f"{config.data_dir}/{model_name}"
    os.makedirs(local_save_directory, exist_ok=True)

    print(f"Loading model '{model_name}' ...")

    try:
        model = SentenceTransformer(model_name)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None

    if model is not None:
        try:
            model.save(local_save_directory)
            print(f"Model saved in directory: {local_save_directory}")
        except Exception as e:
            print(f"Error saving model: {e}")

    print("\nProcess completed.")


if __name__ == "__main__":
    main()
