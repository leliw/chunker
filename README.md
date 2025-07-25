# Chunker

The service:

* Chunks markdown text into smaller parts using the `langchain` `RecursiveCharacterTextSplitter`
* Calculates embeddings for each chunk using the `ipipan/silver-retriever-base-v1.1` model
* The chunk size is dependent on the model used, with a maximum of 512 tokens for the `ipipan/silver-retriever-base-v1.1` model

## Usage

### REST API

* `POST /api/chunks` - Accepts a JSON body with a `text` field containing the markdown text to be chunked.
* `POST /api/chunks/with-embeddings` - Accepts a JSON body with a `text` field containing the markdown text to be chunked and embedded, and returns the embeddings for each chunk.
* `POST /api/embeddings/generate` - Accepts a JSON body with a `text` field containing the markdown text to be chunked and embedded.

### Google Cloud Platform Pub/Sub

Input:

* `POST /api/pub-sub/chunks`

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
