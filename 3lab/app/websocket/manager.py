import asyncio, json, threading
from typing import Dict, List
from fastapi import WebSocket
from app.core.embedded_redis import shim

_pubsub = shim.redis.pubsub()
_pubsub.subscribe("ws_notifications")

class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, List[WebSocket]] = {}
        self._listener_started = False

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(user_id, []).append(ws)
        if not self._listener_started:
            asyncio.get_event_loop().create_task(self._listen())
            self._listener_started = True

    def disconnect(self, user_id: int, ws: WebSocket):
        self.active[user_id].remove(ws)
        if not self.active[user_id]:
            self.active.pop(user_id)

    async def _broadcast(self, uid: int, msg: str):
        for ws in self.active.get(uid, []):
            await ws.send_text(msg)

    async def _listen(self):
        def reader():
            for msg in _pubsub.listen():
                if msg["type"] == "message":
                    data = json.loads(msg["data"])
                    asyncio.get_event_loop().create_task(
                        self._broadcast(data["user_id"], json.dumps(data))
                    )
        threading.Thread(target=reader, daemon=True).start()

manager = ConnectionManager()
