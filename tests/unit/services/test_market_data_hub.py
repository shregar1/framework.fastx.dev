"""
Tests for MarketDataHub behaviour (snapshot + incremental streaming).
"""

import asyncio
import time

from services.streams import MarketDataHub, Tick, OrderEvent


def test_market_data_hub_ticks_snapshot_and_updates():
    hub = MarketDataHub()

    async def scenario():
        # Publish a couple of ticks
        await hub.publish_tick(Tick(symbol="AAPL", price=100.0, size=1.0, side="trade", ts=time.time()))
        await hub.publish_tick(Tick(symbol="AAPL", price=101.0, size=2.0, side="trade", ts=time.time()))

        # Subscribe and ensure we get a snapshot then updates
        gen = hub.subscribe_ticks("AAPL")
        frame_type, payload = await gen.__anext__()
        assert frame_type == "snapshot"
        assert len(payload) == 2

        await hub.publish_tick(Tick(symbol="AAPL", price=102.0, size=3.0, side="trade", ts=time.time()))
        frame_type2, payload2 = await gen.__anext__()
        assert frame_type2 == "update"
        assert isinstance(payload2, Tick)
        assert payload2.price == 102.0

    asyncio.run(scenario())


def test_market_data_hub_orders_snapshot_and_updates():
    hub = MarketDataHub()

    async def scenario():
        tenant_id = "t1"
        await hub.publish_order(
            OrderEvent(
                tenant_id=tenant_id,
                order_id="o1",
                symbol="AAPL",
                side="buy",
                status="new",
                ts=time.time(),
                data={},
            )
        )

        gen = hub.subscribe_orders(tenant_id)
        frame_type, payload = await gen.__anext__()
        assert frame_type == "snapshot"
        assert len(payload) == 1

        await hub.publish_order(
            OrderEvent(
                tenant_id=tenant_id,
                order_id="o1",
                symbol="AAPL",
                side="buy",
                status="filled",
                ts=time.time(),
                data={},
            )
        )
        frame_type2, payload2 = await gen.__anext__()
        assert frame_type2 == "update"
        assert isinstance(payload2, OrderEvent)
        assert payload2.status == "filled"

    asyncio.run(scenario())

