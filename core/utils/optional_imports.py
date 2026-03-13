from __future__ import annotations

from importlib import import_module
from typing import Any, Tuple


def optional_import(module: str, attr: str | None = None) -> Tuple[Any | None, Any | None]:
    """
    Best-effort import helper for optional dependencies.

    Returns a tuple of (module_or_None, attribute_or_None). If the import
    fails for any reason, both values are None.
    """
    try:
        mod = import_module(module)
    except Exception:  # pragma: no cover - optional
        return None, None

    if not attr:
        return mod, None

    current: Any = mod
    for part in attr.split("."):
        try:
            current = getattr(current, part)
        except AttributeError:  # pragma: no cover - defensive
            return mod, None
    return mod, current


__all__ = ["optional_import"]

