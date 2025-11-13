from ampf.gcp import GcpPubsubRequest, gcp_pubsub_process_push
from dependencies import ChunkEmbeddingRequestMessageRouterDep, ChunkRequestMessageRouterDep
from fastapi import APIRouter

router = APIRouter(tags=["Pub/Sub Push"])


@router.post("/requests")
async def handle_push(processor: ChunkRequestMessageRouterDep, request: GcpPubsubRequest):
    return await gcp_pubsub_process_push(processor, request)


@router.post("/requests/embeddings")
async def handle_push_embeddings(processor: ChunkEmbeddingRequestMessageRouterDep, request: GcpPubsubRequest):
    return await gcp_pubsub_process_push(processor, request)
