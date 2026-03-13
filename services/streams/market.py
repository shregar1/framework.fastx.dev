"""
Market data / event streaming hub.

Maintains in-memory tick history per symbol and order events per tenant,
and provides snapshot + incremental streaming semantics that can be used
from WebSocket endpoints.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Any, AsyncGenerator, Deque, Dict, List, Tuple

from loguru import logger

from configurations.streams import StreamsConfiguration
from services.queues import QueueBroker
from .abstractions import OrderEvent, Tick


class MarketDataHub:
    """
    Central hub for ticks and order events.
    """

    def __init__(self) -> None:
        cfg = StreamsConfiguration.instance().get_config()
        self._enabled = cfg.enabled
        self._tick_history = max(1, cfg.tick_history)
        self._fanout_backend = cfg.fanout_queue_backend
        self._backpressure_mode = cfg.backpressure_mode
        self._symbol_ticks: Dict[str, Deque[Tick]] = {}
        self._symbol_subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._tenant_orders: Dict[str, Deque[OrderEvent]] = {}
        self._tenant_subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._queue_broker: QueueBroker | None = None
        if self._fanout_backend:
            try:
                self._queue_broker = QueueBroker()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(f"Failed to initialize QueueBroker for streams fan-out: {exc}")
                self._queue_broker = None

    async def _publish_to_channel(
        self,
        history_store: Dict[str, Deque[Any]],
        subscribers_store: Dict[str, List[asyncio.Queue]],
        key: str,
        event: Any,
        queue_body: Dict[str, Any] | None = None,
        context_label: str = "streams",
    ) -> None:
        """
        Internal helper that appends to history, optionally fans out to a queue backend,
        and notifies all subscribers with backpressure.
        """
        dq = history_store.setdefault(key, deque(maxlen=self._tick_history))
        dq.append(event)

        if queue_body and self._queue_broker and self._fanout_backend:
            try:
                await self._queue_broker.publish(
                    backend=self._fanout_backend,
                    body=queue_body,
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    f"Streams fan-out ({context_label}) to {self._fanout_backend} failed: {exc}"
                )

        for q in list(subscribers_store.get(key, [])):
            await self._push_with_backpressure(q, ("update", event))

    async def publish_tick(self, tick: Tick) -> None:
        if not self._enabled:
            return
        queue_body: Dict[str, Any] | None = None
        if self._fanout_backend:
            queue_body = {
                "type": "tick",
                "symbol": tick.symbol,
                "price": tick.price,
                "size": tick.size,
                "side": tick.side,
                "ts": tick.ts,
            }
        await self._publish_to_channel(
            history_store=self._symbol_ticks,
            subscribers_store=self._symbol_subscribers,
            key=tick.symbol,
            event=tick,
            queue_body=queue_body,
            context_label="ticks",
        )

    async def snapshot_ticks(self, symbol: str) -> List[Tick]:
        return list(self._symbol_ticks.get(symbol, []))

    async def subscribe_ticks(self, symbol: str) -> AsyncGenerator[Tuple[str, Any], None]:
        """
        Yields a ("snapshot", [Tick...]) frame followed by ("update", Tick) frames.
        """
        q: asyncio.Queue = asyncio.Queue()
        subs = self._symbol_subscribers.setdefault(symbol, [])
        subs.append(q)
        try:
            snapshot = await self.snapshot_ticks(symbol)
            yield ("snapshot", snapshot)
            while True:
                msg = await q.get()
                yield msg
        finally:
            if q in subs:
                subs.remove(q)

    async def publish_order(self, event: OrderEvent) -> None:
        if not self._enabled:
            return
        queue_body: Dict[str, Any] | None = None
        if self._fanout_backend:
            queue_body = {
                "type": "order",
                "tenantId": event.tenant_id,
                "orderId": event.order_id,
                "symbol": event.symbol,
                "side": event.side,
                "status": event.status,
                "ts": event.ts,
                "data": event.data,
            }
        await self._publish_to_channel(
            history_store=self._tenant_orders,
            subscribers_store=self._tenant_subscribers,
            key=event.tenant_id,
            event=event,
            queue_body=queue_body,
            context_label="orders",
        )

    async def snapshot_orders(self, tenant_id: str) -> List[OrderEvent]:
        return list(self._tenant_orders.get(tenant_id, []))

    async def subscribe_orders(self, tenant_id: str) -> AsyncGenerator[Tuple[str, Any], None]:
        """
        Yields a ("snapshot", [OrderEvent...]) frame followed by ("update", OrderEvent) frames.
        """
        q: asyncio.Queue = asyncio.Queue()
        subs = self._tenant_subscribers.setdefault(tenant_id, [])
        subs.append(q)
        try:
            snapshot = await self.snapshot_orders(tenant_id)
            yield ("snapshot", snapshot)
            while True:
                msg = await q.get()
                yield msg
        finally:
            if q in subs:
                subs.remove(q)

    async def _push_with_backpressure(self, q: asyncio.Queue, item: Any) -> None:
        if self._backpressure_mode == "last_value":
            # Drop intermediate items and keep only the latest if queue is congested
            if not q.empty():
                try:
                    _ = q.get_nowait()
                except Exception:
                    pass
        await q.put(item)


# Singleton hub instance for application use
_hub: MarketDataHub | None = None


def get_market_data_hub() -> MarketDataHub:
    global _hub
    if _hub is None:
        _hub = MarketDataHub()
    return _hub


__all__ = [
    "Tick",
    "OrderEvent",
    "MarketDataHub",
    "get_market_data_hub",
]

