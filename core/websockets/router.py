"""
Basic WebSocket support for FastMVC.

Provides:
- An echo endpoint at `/ws/echo` for quick testing
- A simple room-based endpoint at `/ws/rooms/{room_id}` that integrates with
  the PresenceService to track active users per room.
"""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.channels.presence import InMemoryPresenceBackend, PresenceService


router = APIRouter(tags=["WebSockets"])

# In-memory connections per room. For production you can replace this with
# a more robust hub or use one of the Channels backends (Pusher/Ably/etc.).
_room_connections: Dict[str, List[WebSocket]] = {}
_presence = PresenceService(InMemoryPresenceBackend(ttl_seconds=60))


@router.websocket("/ws/echo")
async def websocket_echo(ws: WebSocket) -> None:
    """
    Simple echo WebSocket endpoint for smoke testing.
    """
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(data)
    except WebSocketDisconnect:
        return


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(ws: WebSocket, room_id: str) -> None:
    """
    Basic room WebSocket endpoint.

    The client should send an initial JSON message like:
        {"type": "join", "userId": "user-123"}

    Subsequent messages with:
        {"type": "message", "userId": "...", "text": "..."}

    are broadcast to all connected clients in the same room.
    """
    await ws.accept()
    connections = _room_connections.setdefault(room_id, [])
    connections.append(ws)
    user_id: str = "anonymous"

    try:
        # First message is expected to carry user identity
        first = await ws.receive_json()
        if isinstance(first, dict) and first.get("userId"):
            user_id = str(first["userId"])
        await _presence.mark_present(room_id, user_id)

        while True:
            msg = await ws.receive_json()
            msg_type = msg.get("type")
            if msg_type == "message":
                payload = {
                    "roomId": room_id,
                    "userId": msg.get("userId", user_id),
                    "text": msg.get("text", ""),
                }
                for conn in list(connections):
                    try:
                        await conn.send_json(payload)
                    except Exception:
                        # Drop broken connections
                        if conn in connections:
                            connections.remove(conn)
            else:
                # Unknown control messages are ignored for now
                continue
    except WebSocketDisconnect:
        await _presence.mark_absent(room_id, user_id)
        if ws in connections:
            connections.remove(ws)
        if not connections and room_id in _room_connections:
            _room_connections.pop(room_id, None)
        return


__all__ = ["router"]

