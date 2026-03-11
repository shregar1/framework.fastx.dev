"""
LLM provider abstraction.

Supports OpenAI, Anthropic, and local/Ollama-style models via a common
``ILLMService`` interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from loguru import logger

from configurations.llm import LLMConfiguration

try:  # Optional providers
    import openai
except Exception:  # pragma: no cover - optional
    openai = None  # type: ignore

try:
    import anthropic
except Exception:  # pragma: no cover - optional
    anthropic = None  # type: ignore

try:
    import httpx
except Exception:  # pragma: no cover - optional
    httpx = None  # type: ignore


class ILLMService(ABC):
    """
    Minimal LLM service interface.
    """

    @abstractmethod
    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class OpenAILLMService(ILLMService):
    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        if openai is None:  # pragma: no cover - optional
            raise RuntimeError("openai library is not installed")
        client_kwargs: Dict[str, Any] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        self._client = openai.AsyncOpenAI(**client_kwargs)  # type: ignore[attr-defined]
        self._model = model

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        choice = resp.choices[0].message.content or ""
        return choice


class AnthropicLLMService(ILLMService):
    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        if anthropic is None:  # pragma: no cover - optional
            raise RuntimeError("anthropic library is not installed")
        client_kwargs: Dict[str, Any] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        self._client = anthropic.AsyncAnthropic(**client_kwargs)  # type: ignore[attr-defined]
        self._model = model

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        resp = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = resp.content or []
        text_parts: List[str] = []
        for p in parts:
            if getattr(p, "type", None) == "text":
                text_parts.append(getattr(p, "text", ""))
        return "".join(text_parts)


class OllamaLLMService(ILLMService):
    def __init__(self, base_url: str, model: str) -> None:
        if httpx is None:  # pragma: no cover - optional
            raise RuntimeError("httpx library is not installed")
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        url = f"{self._base_url}/api/generate"
        payload = {"model": self._model, "prompt": prompt, "stream": False}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        return data.get("response", "")


def build_llm_service() -> Optional[ILLMService]:
    """
    Build an LLM service instance from configuration.

    Priority:
      - OpenAI
      - Anthropic
      - Ollama
    """

    cfg = LLMConfiguration.instance().get_config()

    if cfg.openai.enabled and cfg.openai.api_key:
        try:
            return OpenAILLMService(
                api_key=cfg.openai.api_key,
                base_url=cfg.openai.base_url,
                model=cfg.openai.model,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize OpenAI LLM service: %s", exc)

    if cfg.anthropic.enabled and cfg.anthropic.api_key:
        try:
            return AnthropicLLMService(
                api_key=cfg.anthropic.api_key,
                base_url=cfg.anthropic.base_url,
                model=cfg.anthropic.model,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Anthropic LLM service: %s", exc)

    if cfg.ollama.enabled:
        try:
            return OllamaLLMService(
                base_url=cfg.ollama.base_url,
                model=cfg.ollama.model,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Ollama LLM service: %s", exc)

    logger.info("No LLM provider is enabled.")
    return None


__all__ = [
    "ILLMService",
    "OpenAILLMService",
    "AnthropicLLMService",
    "OllamaLLMService",
    "build_llm_service",
]

