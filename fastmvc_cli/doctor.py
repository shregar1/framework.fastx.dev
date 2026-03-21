"""
`fastmvc doctor` — environment and dependency sanity checks.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Iterable


def _ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def _warn(msg: str) -> None:
    print(f"  ⚠ {msg}")


def _fail(msg: str) -> None:
    print(f"  ✗ {msg}")


def _can_import(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _check_imports(packages: Iterable[str]) -> tuple[int, int]:
    ok, bad = 0, 0
    for pkg in packages:
        if _can_import(pkg):
            _ok(f"import {pkg}")
            ok += 1
        else:
            _fail(f"missing package: {pkg} (pip install {pkg})")
            bad += 1
    return ok, bad


def _database_url_from_env() -> str | None:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return url
    host = os.environ.get("DATABASE_HOST", "").strip()
    if not host:
        return None
    port = os.environ.get("DATABASE_PORT", "5432")
    name = os.environ.get("DATABASE_NAME", "postgres")
    user = os.environ.get("DATABASE_USER", "postgres")
    password = os.environ.get("DATABASE_PASSWORD", "")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


def run_doctor(
    *,
    project_dir: Path | None = None,
    check_db: bool = False,
    load_dotenv_file: bool = True,
) -> int:
    """
    Run checks. Returns 0 if no failures, 1 if any hard failure.

    Optional DB check uses ``DATABASE_URL`` or ``DATABASE_*`` after loading ``.env``
    when ``load_dotenv_file`` is True.
    """
    root = (project_dir or Path.cwd()).resolve()
    print()
    print(f"FastMVC doctor — {root}")
    print()

    issues = 0

    # Python version
    vi = sys.version_info
    if vi >= (3, 10):
        _ok(f"Python {vi.major}.{vi.minor}.{vi.micro} (>= 3.10)")
    else:
        _fail(f"Python {vi.major}.{vi.minor}.{vi.micro} — FastMVC requires Python 3.10+")
        issues += 1

    # Core runtime imports (what pyfastmvc typically needs)
    _, missing = _check_imports(
        (
            "click",
            "fastapi",
            "pydantic",
            "starlette",
            "uvicorn",
            "sqlalchemy",
            "dotenv",
        )
    )
    issues += missing

    if _can_import("fastmiddleware"):
        _ok("import fastmiddleware")
    else:
        _warn("import fastmiddleware — optional; install fastmvc-middleware stack if you use bundled middlewares")

    # Project-ish layout
    app_py = root / "app.py"
    if app_py.is_file():
        _ok("found app.py (looks like a FastMVC / FastAPI project root)")
        env_file = root / ".env"
        env_example = root / ".env.example"
        if env_file.is_file():
            _ok(".env present")
        else:
            _warn(".env missing — copy from .env.example if you use env-based config")
        if env_example.is_file():
            _ok(".env.example present")
    else:
        _warn("no app.py here — run doctor from a generated project root for env checks")

    if load_dotenv_file:
        try:
            from dotenv import load_dotenv

            loaded = load_dotenv(root / ".env")
            if (root / ".env").is_file():
                _ok(f"python-dotenv loaded .env ({'ok' if loaded else 'empty or skipped'})")
        except Exception as e:
            _warn(f"could not load .env: {e}")

    if check_db:
        print()
        print("Database check (--check-db)")
        url = _database_url_from_env()
        if not url:
            _warn("no DATABASE_URL or DATABASE_HOST — set env or use .env")
        else:
            try:
                from sqlalchemy import create_engine, text

                eng = create_engine(url, pool_pre_ping=True)
                with eng.connect() as conn:
                    conn.execute(text("SELECT 1"))
                _ok("database: SELECT 1 succeeded")
            except Exception as e:
                _fail(f"database check failed: {e}")
                issues += 1

    print()
    if issues:
        print(f"Doctor finished with {issues} error(s).")
        return 1
    print("Doctor: all critical checks passed.")
    return 0


def export_openapi_json(project_dir: Path, out_name: str = "openapi.json") -> tuple[bool, str]:
    """
    Write OpenAPI schema to *out_name* under *project_dir*.

    Runs a subprocess so a broken app import does not crash the CLI process.
    """
    project_dir = project_dir.resolve()
    out_path = project_dir / out_name
    script = (
        "import json\n"
        "from pathlib import Path\n"
        "from app import app\n"
        f"Path({str(out_path)!r}).write_text(json.dumps(app.openapi(), indent=2))\n"
    )
    try:
        import subprocess

        r = subprocess.run(
            [sys.executable, "-c", script],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "PYTHONPATH": str(project_dir)},
        )
        if r.returncode != 0:
            return False, (r.stderr or r.stdout or "unknown error").strip()
        if out_path.is_file():
            return True, str(out_path)
        return False, "openapi file was not created"
    except Exception as e:
        return False, str(e)
