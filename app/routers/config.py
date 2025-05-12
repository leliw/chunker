from fastapi import APIRouter

from config import ClientConfig
from dependencies import ConfigDep

router = APIRouter(tags=["Client config"])


@router.get("")
async def get_client_config(config: ConfigDep) -> ClientConfig:
    return ClientConfig(**config.model_dump())
