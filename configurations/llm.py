"""
Singleton configuration loader for LLM providers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from dtos.configurations.llm import LLMConfigurationDTO


class LLMConfiguration:
    """
    Lazily loads LLM configuration from ``config/llm/config.json``.
    """

    _instance: Optional["LLMConfiguration"] = None

    def __init__(self) -> None:
        base_path = Path(__file__).resolve().parent.parent
        config_path = base_path / "config" / "llm" / "config.json"
        raw = {}
        if config_path.exists():
            raw = json.loads(config_path.read_text())

        self._config = LLMConfigurationDTO(**raw)

    @classmethod
    def instance(cls) -> "LLMConfiguration":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_config(self) -> LLMConfigurationDTO:
        return self._config


__all__ = [
    "LLMConfiguration",
]

