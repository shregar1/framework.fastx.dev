"""
Configuration DTOs for market data / event streams.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class StreamsConfigurationDTO(BaseModel):
    enabled: bool = False
    tick_history: int = 200
    max_fanout_per_symbol: int = 1000
    coalesce_ms: int = 0
    backpressure_mode: Literal["immediate", "last_value"] = "immediate"
    fanout_queue_backend: Optional[str] = None  # e.g. "rabbitmq", "sqs", "nats"


__all__ = ["StreamsConfigurationDTO"]

