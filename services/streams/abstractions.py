"""
Abstractions for high-frequency market data and generic event streams.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List


@dataclass
class Tick:
    symbol: str
    price: float
    size: float
    side: str  # "bid" / "ask" / "trade"
    ts: float


@dataclass
class OrderEvent:
    tenant_id: str
    order_id: str
    symbol: str
    side: str  # "buy" / "sell"
    status: str  # "new" / "filled" / "canceled" / ...
    ts: float
    data: Dict[str, Any]


class IMarketDataFeed(ABC):
    """
    Interface for external market data providers (Kafka, Redis streams, FIX, etc.).
    """

    @abstractmethod
    async def run(self, hub: "MarketDataHub") -> None:  # pragma: no cover - interface
        """
        Connect to an external feed and push ticks into the hub.
        """


class IEventStream(ABC):
    """
    Generic high-frequency event stream abstraction.
    """

    @abstractmethod
    async def publish(self, event: Any) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    @abstractmethod
    async def subscribe(self) -> AsyncGenerator[Any, None]:  # pragma: no cover - interface
        raise NotImplementedError


__all__ = [
    "Tick",
    "OrderEvent",
    "IMarketDataFeed",
    "IEventStream",
]

