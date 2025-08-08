# Chunker

A FastAPI-based microservice responsible for chunking markdowns and calculating embeddings.

---

## Overview

The **Chunker Service** handles core functionality such as:

* Chunks markdown text into smaller parts using the `langchain` `RecursiveCharacterTextSplitter`
* Calculates embeddings for each chunk using the `ipipan/silver-retriever-base-v1.1` model
* The chunk size is dependent on the model used, with a maximum of 512 tokens for the `ipipan/silver-retriever-base-v1.1` model

It is designed to be stateless and scalable as part of a microservices architecture.

---

## Architecture & Dependencies

* **Package manager**: uv
* **Framework**: FastAPI
* **Web server**: Uvicorn / Gunicorn
* **Authentication**: `x_api_key` header (optional)
* **Chunking**: `langchain` library with `RecursiveCharacterTextSplitter`
* **Embeddings**: `ipipan/silver-retriever-base-v1.1` model from Hugging Face
* **Database**: None (stateless service)
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

### Google Cloud Platform Pub/Sub

Input:

* `POST /pub-sub/reqests`

```python
class ChunksRequest(BaseModel):
    page_id: UUID
    text: str
```

Output (first defined is used):

* Topic defined in message in `response_topic` attribute
* Topic defined in environment in `CHUNKS_RESPONSE_TOPIC` variable
* Topic defined in environment with `sender_id` defined in message

```python
class ChunkWithEmmebeddings(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    page_id: UUID
    task_id: Optional[UUID] = None
    chunk_index: int
    language: str
    text: str
    token_count: Optional[int] = None
    embedding: List[float]
    created_at: datetime = datetime.now(timezone.utc)
```
