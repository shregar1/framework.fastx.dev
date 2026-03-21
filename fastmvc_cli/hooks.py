"""
Optional project hooks (``post_generate``, ``pre_run``) from ``fastmvc.toml`` or
``pyproject.toml`` ``[tool.fastmvc.hooks]``.

Extra hook scripts directory: env ``FASTMVC_HOOKS_PATH`` (``PATH``-style list).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HOOK_KEYS = ("post_generate", "pre_run")


def _loads_toml(raw: bytes) -> dict[str, Any]:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomli as tomllib  # type: ignore[import-not-found]
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "Parsing TOML hooks requires Python 3.11+ or: pip install tomli"
            ) from e
    return tomllib.loads(raw.decode("utf-8"))


def load_hook_config(project_root: Path) -> dict[str, Any]:
    """
    Load hook definitions. Merges ``fastmvc.toml`` and ``[tool.fastmvc]`` from
    ``pyproject.toml`` (later keys override).
    """
    merged: dict[str, Any] = {}
    for name in ("fastmvc.toml", "pyproject.toml"):
        path = project_root / name
        if not path.is_file():
            continue
        try:
            data = _loads_toml(path.read_bytes())
        except Exception:
            continue
        if name == "pyproject.toml":
            tool = data.get("tool") or {}
            fm = tool.get("fastmvc") or {}
            hooks = fm.get("hooks") or {}
            merged.update(hooks)
        else:
            hooks = data.get("hooks") or {}
            merged.update(hooks)

    extra = os.environ.get("FASTMVC_HOOKS_PATH", "")
    if extra.strip():
        merged["_extra_plugin_paths"] = [
            Path(p.strip()).expanduser()
            for p in extra.split(os.pathsep)
            if p.strip()
        ]
    return merged


def _normalize_commands(value: Any) -> list[list[str]]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.split()]
    if isinstance(value, (list, tuple)):
        out: list[list[str]] = []
        for item in value:
            if isinstance(item, str):
                out.append(item.split())
            elif isinstance(item, (list, tuple)):
                out.append([str(x) for x in item])
        return out
    return []


def run_hook(
    hook_name: str,
    project_root: Path,
    *,
    env: dict[str, str] | None = None,
) -> None:
    """Run shell commands for ``hook_name`` (``post_generate`` or ``pre_run``)."""
    cfg = load_hook_config(project_root)
    cmds = _normalize_commands(cfg.get(hook_name))
    if not cmds:
        return
    base_env = os.environ.copy()
    if env:
        base_env.update(env)
    base_env.setdefault("FASTMVC_PROJECT_ROOT", str(project_root.resolve()))

    for argv in cmds:
        if not argv:
            continue
        subprocess.run(argv, cwd=project_root, env=base_env, check=True)


def run_post_generate(project_root: Path) -> None:
    run_hook("post_generate", project_root)


def run_pre_run(project_root: Path) -> None:
    run_hook("pre_run", project_root)
