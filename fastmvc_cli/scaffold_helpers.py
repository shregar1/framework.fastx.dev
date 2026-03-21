"""Shared file writers for ``fastmvc generate`` / ``fastmvc init``."""

from __future__ import annotations

from pathlib import Path


def write_license(path: Path, license_key: str, project: str) -> None:
    year = str(Path().stat().st_mtime_ns)[:4]
    if license_key == "mit":
        text = f"""MIT License

Copyright (c) {year} {project}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    elif license_key == "apache-2.0":
        text = f"""Apache License 2.0

Copyright (c) {year} {project}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
    elif license_key == "gpl-3.0":
        text = f"""GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Copyright (c) {year} {project}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""
    else:  # proprietary
        text = f"""All Rights Reserved

Copyright (c) {year} {project}

This software is proprietary and confidential. Unauthorized copying of this
file, via any medium is strictly prohibited.
"""
    path.write_text(text)


def write_contributing(path: Path) -> None:
    text = """# Contributing

1. Fork the repository and create a feature branch.
2. Install dependencies and pre-commit hooks.
3. Run tests and linters before opening a pull request.

```bash
pip install -r requirements.txt
pytest
```
"""
    path.write_text(text)


def write_codeowners(path: Path, owner: str) -> None:
    if owner:
        path.write_text(f"* {owner}\n")


def write_pyproject(
    path: Path,
    use_ruff: bool,
    use_black: bool,
    use_isort: bool,
    use_mypy: bool,
) -> None:
    """Create a minimal pyproject.toml with tool configs."""
    lines: list[str] = []
    if use_black:
        lines.extend(
            [
                "[tool.black]",
                'line-length = 88',
                'target-version = ["py310"]',
                "",
            ]
        )
    if use_isort:
        lines.extend(
            [
                "[tool.isort]",
                'profile = "black"',
                "",
            ]
        )
    if use_ruff:
        lines.extend(
            [
                "[tool.ruff]",
                "line-length = 88",
                'target-version = "py310"',
                "",
            ]
        )
    if use_mypy:
        lines.extend(
            [
                "[tool.mypy]",
                "python_version = 3.10",
                "ignore_missing_imports = true",
                "",
            ]
        )
    if lines:
        path.write_text("\n".join(lines))


def write_precommit(
    path: Path,
    use_ruff: bool,
    use_black: bool,
    use_isort: bool,
    use_mypy: bool,
) -> None:
    """Create a basic .pre-commit-config.yaml."""
    repos: list[str] = ["repos:"]
    if use_black:
        repos.extend(
            [
                "- repo: https://github.com/psf/black",
                "  rev: 23.12.1",
                "  hooks:",
                "    - id: black",
                "",
            ]
        )
    if use_ruff:
        repos.extend(
            [
                "- repo: https://github.com/astral-sh/ruff-pre-commit",
                "  rev: v0.5.0",
                "  hooks:",
                "    - id: ruff",
                "",
            ]
        )
    if use_isort:
        repos.extend(
            [
                "- repo: https://github.com/pycqa/isort",
                "  rev: 5.13.2",
                "  hooks:",
                "    - id: isort",
                "",
            ]
        )
    if use_mypy:
        repos.extend(
            [
                "- repo: https://github.com/pre-commit/mirrors-mypy",
                "  rev: v1.11.0",
                "  hooks:",
                "    - id: mypy",
                "",
            ]
        )
    repos.extend(
        [
            "- repo: local",
            "  hooks:",
            "    - id: pytest",
            '      name: pytest',
            '      entry: pytest',
            "      language: system",
            "      types: [python]",
            "",
        ]
    )
    path.write_text("\n".join(repos))


def write_ci_workflow(
    path: Path,
    use_ruff: bool,
    use_black: bool,
    use_isort: bool,
    use_mypy: bool,
) -> None:
    """Create a simple GitHub Actions CI workflow."""
    steps_tools = []
    if use_black:
        steps_tools.append("black .")
    if use_ruff:
        steps_tools.append("ruff .")
    if use_isort:
        steps_tools.append("isort .")
    if use_mypy:
        steps_tools.append("mypy .")

    tools_block = ""
    if steps_tools:
        joined = " && ".join(steps_tools)
        tools_block = f"""
      - name: Run linters/formatters
        run: {joined}
"""

    workflow = f"""name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install pytest pytest-cov ruff black isort mypy
{tools_block}
      - name: Run tests
        run: pytest --cov=. --cov-report=term-missing
"""
    path.write_text(workflow)
