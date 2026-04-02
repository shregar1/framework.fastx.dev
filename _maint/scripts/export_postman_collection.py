#!/usr/bin/env python3
"""Regenerate Postman artifacts using the same export path as app startup.

Writes ``postman/postman_collection.json`` (and optionally
``postman/postman_environment.json``) by importing the live ``app`` module and calling
:class:`RouteExportEngine` — same routes and OpenAPI as ``uvicorn app:app``.

Usage (from repo root, with dependencies installed)::

    python3 _maint/scripts/export_postman_collection.py

Environment variables match :mod:`app` / :mod:`core.route_export_engine` (see README).

"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    root = _repo_root()
    os.chdir(root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Match uvicorn: load ``.env`` before importing ``app`` (config validation, etc.).
    try:
        from dotenv import load_dotenv  # noqa: PLC0415

        load_dotenv(root / ".env")
    except ImportError:
        pass

    # Import after path/cwd so ``app`` resolves like ``uvicorn app:app``
    import app as app_module  # noqa: PLC0415

    engine = app_module.route_export_engine
    engine.build_curl_examples()
    collection_path, env_path = engine.export_postman_collection()
    engine.clear_memory()

    print(f"Wrote Postman collection: {collection_path.resolve()}")
    if env_path is not None:
        print(f"Wrote Postman environment: {env_path.resolve()}")
    else:
        print(
            "Environment file skipped (set POSTMAN_EXPORT_ENVIRONMENT=1 to also write it)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
