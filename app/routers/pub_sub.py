import base64
import logging
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

_log = logging.getLogger(__name__)

router = APIRouter(tags=["Pub/Sub Push"])


class PubsubMessage(BaseModel):
    attributes: Optional[Dict[str, str]] = None
    data: str
    messageId: Optional[str] = None
    publishTime: Optional[str] = None


class PushRequest(BaseModel):
    message: PubsubMessage
    subscription: str


@router.post("")
async def handle_push(request: PushRequest):
    try:
        encoded_data = request.message.data
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        _log.info("Received: %s ID: %s", request.subscription, request.message.messageId)
        _log.debug("Data: %s", decoded_data)

        return {"status": "acknowledged", "messageId": request.message.messageId}
    except Exception as e:
        _log.error("Error processing message ID: %s: %s", request.message.messageId, e)
        raise HTTPException(status_code=500, detail=f"Error processing message: {e}")
