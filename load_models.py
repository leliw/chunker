import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Add the 'app' directory to the Python path to allow imports from 'app'
# This makes the script runnable from the project root directory.
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app_config import AppConfig

def main():
    load_dotenv()
    
    config = AppConfig()
    if not config.model_names:
        print("No models configured in 'model_names'. Exiting.")
        return

    for model_name in config.model_names:
        local_save_directory = f"{config.data_dir}/{model_name}"
        os.makedirs(local_save_directory, exist_ok=True)

        print(f"Loading model '{model_name}' ...")

        try:
            model = SentenceTransformer(model_name)
            print(f"Model '{model_name}' loaded successfully.")
        except Exception as e:
            print(f"Error loading model '{model_name}': {e}")
            continue  # Skip to the next model on error

        try:
            model.save(local_save_directory)
            print(f"Model '{model_name}' saved in directory: {local_save_directory}")
        except Exception as e:
            print(f"Error saving model '{model_name}': {e}")

    print("\nProcess completed.")


if __name__ == "__main__":
    main()
