from dotenv import load_dotenv
from fastapi import FastAPI

from dependencies import lifespan
from log_config import setup_logging
from routers import (
    config,
)

load_dotenv()
setup_logging()
app = FastAPI(lifespan=lifespan)


# Include the client config router
app.include_router(config.router, prefix="/api/config")
