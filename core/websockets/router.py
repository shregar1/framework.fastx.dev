"""Basic WebSocket support for FastMVC.

Provides:
- An echo endpoint at `/ws/echo` for quick testing
- A simple room-based endpoint at `/ws/rooms/{room_id}` that integrates with
  the PresenceService to track active users per room.
"""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List, Tuple

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from fast_channels import InMemoryPresenceBackend, PresenceService
from services.streams import Tick, OrderEvent, get_market_data_hub


router = APIRouter(tags=["WebSockets"])

# In-memory connections per room. For production you can replace this with
# a more robust hub or use one of the Channels backends (Pusher/Ably/etc.).
_room_connections: Dict[str, List[WebSocket]] = {}
_presence = PresenceService(InMemoryPresenceBackend(ttl_seconds=60))
_market_hub = get_market_data_hub()


async def _stream_frames(
    ws: WebSocket,
    gen: AsyncGenerator[Tuple[str, Any], None],
    snapshot_serializer: callable,
    update_serializer: callable,
) -> None:
    """Helper to stream snapshot + update frames over a WebSocket.

    Expects the generator to yield (frame_type, payload) tuples where
    frame_type is "snapshot" or "update".
    """
    await ws.accept()
    try:
        async for frame_type, payload in gen:
            if frame_type == "snapshot":
                await ws.send_json(snapshot_serializer(payload))
            else:
                await ws.send_json(update_serializer(payload))
    except WebSocketDisconnect:
        return


@router.websocket("/ws/echo")
async def websocket_echo(ws: WebSocket) -> None:
    """Simple echo WebSocket endpoint for smoke testing."""
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(data)
    except WebSocketDisconnect:
        return


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(ws: WebSocket, room_id: str) -> None:
    """Basic room WebSocket endpoint.

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


@router.websocket("/ws/market/{symbol}")
async def websocket_market(ws: WebSocket, symbol: str) -> None:
    """Low-latency market data feed for a given symbol.

    Sends an initial snapshot frame:
        {"type": "snapshot", "ticks": [...]}

    Followed by incremental updates:
        {"type": "update", "tick": {...}}
    """
    hub = _market_hub

    def snapshot_serializer(payload: Any) -> Dict[str, Any]:
        """Execute snapshot_serializer operation.

        Args:
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        ticks = [
            {
                "symbol": t.symbol,
                "price": t.price,
                "size": t.size,
                "side": t.side,
                "ts": t.ts,
            }
            for t in payload
        ]
        return {"type": "snapshot", "symbol": symbol, "ticks": ticks}

    def update_serializer(payload: Any) -> Dict[str, Any]:
        """Execute update_serializer operation.

        Args:
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        t: Tick = payload
        return {
            "type": "update",
            "symbol": t.symbol,
            "tick": {
                "price": t.price,
                "size": t.size,
                "side": t.side,
                "ts": t.ts,
            },
        }

    await _stream_frames(
        ws, hub.subscribe_ticks(symbol), snapshot_serializer, update_serializer
    )


@router.websocket("/ws/orders/{tenant_id}")
async def websocket_orders(ws: WebSocket, tenant_id: str) -> None:
    """Stream order/position events per tenant.

    Snapshot:
        {"type": "snapshot", "orders": [...]}
    Updates:
        {"type": "update", "order": {...}}
    """
    hub = _market_hub

    def snapshot_serializer(payload: Any) -> Dict[str, Any]:
        """Execute snapshot_serializer operation.

        Args:
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        orders = [
            {
                "tenantId": o.tenant_id,
                "orderId": o.order_id,
                "symbol": o.symbol,
                "side": o.side,
                "status": o.status,
                "ts": o.ts,
                "data": o.data,
            }
            for o in payload
        ]
        return {"type": "snapshot", "tenantId": tenant_id, "orders": orders}

    def update_serializer(payload: Any) -> Dict[str, Any]:
        """Execute update_serializer operation.

        Args:
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        o: OrderEvent = payload
        return {
            "type": "update",
            "tenantId": o.tenant_id,
            "order": {
                "orderId": o.order_id,
                "symbol": o.symbol,
                "side": o.side,
                "status": o.status,
                "ts": o.ts,
                "data": o.data,
            },
        }

    await _stream_frames(
        ws, hub.subscribe_orders(tenant_id), snapshot_serializer, update_serializer
    )


__all__ = ["router"]
