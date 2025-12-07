# live_log_bus.py
from typing import List, Dict, Any
from fastapi import WebSocket

subscribers: List[WebSocket] = []


async def register(ws: WebSocket):
    subscribers.append(ws)


async def unregister(ws: WebSocket):
    if ws in subscribers:
        subscribers.remove(ws)


async def broadcast(event: Dict[str, Any]):
    dead = []
    for ws in subscribers:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)

    for ws in dead:
        if ws in subscribers:
            subscribers.remove(ws)
