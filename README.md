# Chunker

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI Version](https://img.shields.io/badge/FastAPI-0.116%2B-009688.svg)
![uv Package Manager](https://img.shields.io/badge/Package%20Manager-uv-purple.svg)
![License](https://img.shields.io/badge/License-MIT-lightgray.svg)

A FastAPI-based microservice responsible for chunking markdowns and calculating embeddings.

## Overview

The **Chunker Service** handles core functionality such as:

* Chunks markdown text into smaller parts using the `langchain` `RecursiveCharacterTextSplitter`
* Calculates embeddings for each chunk using the `ipipan/silver-retriever-base-v1.1` for polish lanquage or `Qwen/Qwen3-Embedding-0.6B` for english language
* Detects the language of the input text using the `lingua-language-detector` library
* The chunk size is dependent on the model used

It is designed to be stateless and scalable as part of a microservices architecture.

## Architecture & Dependencies

* **Package manager**: uv
* **Framework**: FastAPI
* **Web server**: Uvicorn / Gunicorn
* **Authentication**: `x_api_key` header (optional)
* **Chunking**: `langchain` library with `RecursiveCharacterTextSplitter`
* **Embeddings**: `ipipan/silver-retriever-base-v1.1` and `Qwen/Qwen3-Embedding-0.6B` models from Hugging Face
* **Language detection**: `lingua-language-detector` library
* **Database**: None (stateless service)
* **Message Queue**: Google Cloud Pub/Sub (optional)
* **Containerization**: Docker
* **Testing**: Pytest

## Build and Run

To build and run the service, you can use Docker. The service is available in two versions: `cpu` and `gpu`. You can build the image using the provided `docker_build.sh` script.

```bash
source ./docker_build.sh
```

To run the service locally, you can run the following command:

```bash
source ./run_dev.sh
```

To run dockerized version of the service, you can use the following command:

```bash
source ./run_docker.sh
```

## API Documentation

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* OpenAPI spec: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Configuration

The application can be configured using environment variables. A .env file is supported for local development.
Example .env file:

```dotenv
PYTHONPATH=app

GOOGLE_CLOUD_PROJECT=
```

All configuration options can be found in `app/config.py` in `ServerConfig` class.

* `data_dir`: Directory to store application data (embedings models)
* `model_names`: Comma-separated list of model names to load
* `default_model_for_language`: Default model to use for a given language  
* `api_key`: API key for authenticating requests
* `chunks_embedding_at_once`: Number of text chunks to embed in a single request, if more chunks are generated, they will be processed asynchronously by pub/sub topic
* `request_embeddings_topic`: Pub/Sub topic for processing embedding requests
* `chunks_response_topic`: Default Pub/Sub topic for returning chunks

Logging configuration options can be found in `app/logging_config.py` in `LogConfig` class (below `# Loggers` comment).
Environment variables should be prefixed with `LOG_`, e.g. `LOG_LOG_CONFIG=DEBUG` for `log_config` logger.

* log_config
* routers__pub_sub
* features__embeddings__embedding_service

Make sure to set these environment variables in your deployment environment. Never commit sensitive information like SECRET_KEY directly into your repository.

### REST API

* `POST /api/chunks` - Accepts a JSON body with a `text` field containing the markdown text to be chunked.
* `POST /api/chunks/with-embeddings` - Accepts a JSON body with a `text` field containing the markdown text to be chunked and embedded, and returns the embeddings for each chunk.
* `POST /api/embeddings/generate` - Accepts a JSON body with a `text` field containing the markdown text to be chunked and embedded.
* `POST /api/embeddings/generate/query` - Accepts a JSON body with a `text` field containing the **query** text to be embedded.
* `POST /api/embeddings/generate/passage` - Accepts a JSON body with a `title` and `text` field containing the **passage** of text to be embedded.

### Google Cloud Platform Pub/Sub

#### POST /pub-sub/reqests

Splits the provided text into chunks and generates embeddings for each chunk.

```python
# app/features/chunks/chunk_model.py

class ChunksRequest(BaseModel):
    job_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    language: Optional[str] = None
    embedding_model_name: Optional[str] = None
    text: Optional[str] = None
    input_file: Optional[GcpFile] = None
    metadata: Optional[Dict[str, str]] = None
```

Output (first defined is used):

* Topic defined in message in `response_topic` attribute
* Topic defined in environment in `CHUNKS_RESPONSE_TOPIC` variable
* Topic defined in environment with `sender_id` defined in message

```python
# app/features/chunks/chunk_model.py

class ChunkWithEmebeddings(BaseModel):
    job_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    chunk_index: int
    total_chunks: int
    language: str
    text: str
    token_count: Optional[int] = None
    embedding: List[float]
    metadata: Optional[Dict[str, str]] = None
    created_at: datetime = datetime.now(timezone.utc)
```

If number of chunks is greater than 4 (`config.chunks_embedding_at_once`)the embeddings are generated in separate steps to avoid timeouts.
Chunks without embeddings are sent to the "chunker-embeddings-requests" topic (`config.embeddings_request_topic`).

#### POST /pub-sub/requests/embeddings

Generates embeddings for the provided chunk of text. Input and output models are the same as in the `ChunkWithEmebeddings` class.
