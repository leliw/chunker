from dependencies import lifespan
from dotenv import load_dotenv
from fastapi import FastAPI
from log_config import setup_logging
from routers import (
    config,
    embeddings,
)

load_dotenv()
setup_logging()
app = FastAPI(lifespan=lifespan)


app.include_router(config.router, prefix="/api/config")
app.include_router(embeddings.router, prefix="/api/embeddings")
