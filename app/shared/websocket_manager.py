from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder


logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections[str(user_id)] = websocket

    async def disconnect(self, user_id: str) -> None:
        async with self._lock:
            self._connections.pop(str(user_id), None)

    async def send_to_user(self, user_id: str, payload: Any) -> bool:
        key = str(user_id)

        async with self._lock:
            websocket = self._connections.get(key)

        if websocket is None:
            return False

        try:
            await websocket.send_json(jsonable_encoder(payload))
        except Exception:
            logger.debug("Removing stale websocket connection for user %s", key, exc_info=True)
            await self.disconnect(key)
            return False

        return True


websocket_manager = WebSocketManager()


__all__ = ["WebSocketManager", "websocket_manager"]
