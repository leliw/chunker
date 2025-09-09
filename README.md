# Chunker

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-blue)

A FastAPI-based microservice responsible for chunking markdowns and calculating embeddings.

---

## Overview

The **Chunker Service** handles core functionality such as:

* Chunks markdown text into smaller parts using the `langchain` `RecursiveCharacterTextSplitter`
* Calculates embeddings for each chunk using the `ipipan/silver-retriever-base-v1.1` for polish lanquage or `Qwen/Qwen3-Embedding-0.6B` for english language
* Detects the language of the input text using the `lingua-language-detector` library
* The chunk size is dependent on the model used

It is designed to be stateless and scalable as part of a microservices architecture.

---

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

---

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
