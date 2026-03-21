"""Optional PyPI version check for ``pyfastmvc`` (stdlib only)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


def fetch_pypi_latest_version(package: str = "pyfastmvc", timeout: float = 5.0) -> str | None:
    """Return latest version string from PyPI JSON API, or None on failure."""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        return str(data.get("info", {}).get("version"))
    except (urllib.error.URLError, json.JSONDecodeError, OSError, TypeError):
        return None
