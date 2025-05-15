from dependencies import lifespan, verify_api_key
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from log_config import setup_logging
from routers import (
    chunks,
    config,
    embeddings,
)

load_dotenv()
setup_logging()
app = FastAPI(
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)]
)


app.include_router(config.router, prefix="/api/config")
app.include_router(embeddings.router, prefix="/api/embeddings")
app.include_router(chunks.router, prefix="/api/chunks")
