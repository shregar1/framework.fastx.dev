"""
Singleton configuration loader for market data / event streams.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from dtos.configurations.streams import StreamsConfigurationDTO


class StreamsConfiguration:
    """
    Lazily loads streams configuration from ``config/streams/config.json``.
    """

    _instance: Optional["StreamsConfiguration"] = None

    def __init__(self) -> None:
        base_path = Path(__file__).resolve().parent.parent
        config_path = base_path / "config" / "streams" / "config.json"
        raw = {}
        if config_path.exists():
            raw = json.loads(config_path.read_text())

        self._config = StreamsConfigurationDTO(**raw)

    @classmethod
    def instance(cls) -> "StreamsConfiguration":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_config(self) -> StreamsConfigurationDTO:
        return self._config


__all__ = ["StreamsConfiguration"]

