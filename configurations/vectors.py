"""
Singleton configuration loader for vector stores.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from dtos.configurations.vectors import VectorsConfigurationDTO


class VectorsConfiguration:
    """
    Lazily loads vector store configuration from ``config/vectors/config.json``.
    """

    _instance: Optional["VectorsConfiguration"] = None

    def __init__(self) -> None:
        base_path = Path(__file__).resolve().parent.parent
        config_path = base_path / "config" / "vectors" / "config.json"
        raw = {}
        if config_path.exists():
            raw = json.loads(config_path.read_text())

        self._config = VectorsConfigurationDTO(**raw)

    @classmethod
    def instance(cls) -> "VectorsConfiguration":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_config(self) -> VectorsConfigurationDTO:
        return self._config


__all__ = [
    "VectorsConfiguration",
]

