"""
FastMVC CLI - Command Line Interface.

This module provides the main CLI entry point for FastMVC framework.
It uses Click for building the command-line interface.

Commands:
    generate: Create a new FastMVC project from template
    add: Add entities, migrations, etc. to existing project
    migrate: Database migration commands
    version: Display the current FastMVC version
    info: Display information about FastMVC

Example:
    $ fastmvc generate my_api
    $ fastmvc add entity Product
    $ fastmvc migrate upgrade
    $ fastmvc version
    $ fastmvc info
"""

import os
import base64
import secrets
import socket
import subprocess
import sys
from pathlib import Path
import shutil

import click

from fastmvc_cli import __version__
from fastmvc_cli.entity_generator import EntityGenerator
from fastmvc_cli.generator import ProjectGenerator


@click.group()
@click.version_option(version=__version__, prog_name="fastmvc")
def cli():
    """
    FastMVC - Production-grade MVC Framework for FastAPI.

    Generate new FastAPI projects with a clean MVC architecture,
    built-in authentication, rate limiting, security headers,
    and comprehensive documentation.

    \b
    Quick Start:
        $ fastmvc generate my_project
        $ cd my_project
        $ pip install -r requirements.txt
        $ python -m uvicorn app:app --reload

    \b
    Add Entities:
        $ cd my_project
        $ fastmvc add entity Product
        $ fastmvc add entity Order

    \b
    Database Migrations:
        $ fastmvc migrate generate "add products table"
        $ fastmvc migrate upgrade
        $ fastmvc migrate downgrade
    """
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--output-dir", "-o",
    default=".",
    help="Directory where the project will be created (default: current directory)"
)
@click.option(
    "--git/--no-git",
    default=True,
    help="Initialize a git repository (default: True)"
)
@click.option(
    "--venv/--no-venv",
    default=False,
    help="Create a virtual environment (default: False)"
)
@click.option(
    "--install/--no-install",
    default=False,
    help="Install dependencies after generation (default: False)"
)
@click.option(
    "--with-redis/--no-redis",
    default=True,
    help="Include Redis cache configuration (default: True)"
)
@click.option(
    "--with-mongo/--no-mongo",
    default=False,
    help="Include MongoDB configuration and helpers (default: False)"
)
@click.option(
    "--with-cassandra/--no-cassandra",
    default=False,
    help="Include Cassandra configuration and helpers (default: False)"
)
@click.option(
    "--with-scylla/--no-scylla",
    default=False,
    help="Include ScyllaDB configuration and helpers (default: False)"
)
@click.option(
    "--with-dynamo/--no-dynamo",
    default=False,
    help="Include DynamoDB configuration and helpers (default: False)"
)
@click.option(
    "--with-cosmos/--no-cosmos",
    default=False,
    help="Include Azure Cosmos DB configuration and helpers (default: False)"
)
@click.option(
    "--with-elasticsearch/--no-elasticsearch",
    default=False,
    help="Include Elasticsearch configuration and helpers (default: False)"
)
@click.option(
    "--with-meilisearch/--no-meilisearch",
    default=False,
    help="Include Meilisearch configuration and helpers (default: False)",
)
@click.option(
    "--with-typesense/--no-typesense",
    default=False,
    help="Include Typesense configuration and helpers (default: False)",
)
@click.option(
    "--with-email/--no-email",
    default=False,
    help="Include email (SMTP/SendGrid) configuration and helpers (default: False)"
)
@click.option(
    "--with-slack/--no-slack",
    default=False,
    help="Include Slack configuration and helpers (default: False)"
)
@click.option(
    "--with-datadog/--no-datadog",
    default=False,
    help="Include Datadog configuration helpers (default: False)"
)
@click.option(
    "--with-telemetry/--no-telemetry",
    default=False,
    help="Include OpenTelemetry configuration helpers (default: False)"
)
@click.option(
    "--with-payments/--no-payments",
    default=False,
    help="Include payment gateway configuration and helpers (default: False)"
)
@click.option(
    "--with-rabbitmq/--no-rabbitmq",
    default=False,
    help="Include RabbitMQ queue configuration and helpers (default: False)",
)
@click.option(
    "--with-sqs/--no-sqs",
    default=False,
    help="Include Amazon SQS queue configuration and helpers (default: False)",
)
@click.option(
    "--with-celery/--no-celery",
    default=False,
    help="Include Celery background worker configuration and helpers (default: False)",
)
@click.option(
    "--with-analytics/--no-analytics",
    default=False,
    help="Include analytics / event tracking configuration (default: False)",
)
@click.option(
    "--with-vault/--no-vault",
    default=False,
    help="Include HashiCorp Vault secrets backend configuration (default: False)",
)
@click.option(
    "--with-aws-secrets/--no-aws-secrets",
    default=False,
    help="Include AWS Secrets Manager backend configuration (default: False)",
)
@click.option(
    "--with-feature-flags/--no-feature-flags",
    default=False,
    help="Include feature flags (LaunchDarkly/Unleash) configuration (default: False)",
)
@click.option(
    "--with-llm/--no-llm",
    default=False,
    help="Include LLM provider configuration and helpers (default: False)",
)
@click.option(
    "--with-pinecone/--no-pinecone",
    default=False,
    help="Include Pinecone vector store configuration and helpers (default: False)",
)
@click.option(
    "--with-qdrant/--no-qdrant",
    default=False,
    help="Include Qdrant vector store configuration and helpers (default: False)",
)
@click.option(
    "--with-s3/--no-s3",
    default=False,
    help="Include AWS S3 object storage configuration and helpers (default: False)",
)
@click.option(
    "--with-gcs/--no-gcs",
    default=False,
    help="Include Google Cloud Storage configuration and helpers (default: False)",
)
@click.option(
    "--with-azure-blob/--no-azure-blob",
    default=False,
    help="Include Azure Blob Storage configuration and helpers (default: False)",
)
@click.option(
    "--with-identity/--no-identity",
    default=False,
    help="Include identity provider / SSO configuration helpers (default: False)",
)
def generate(
    project_name: str,
    output_dir: str,
    git: bool,
    venv: bool,
    install: bool,
    with_redis: bool,
    with_mongo: bool,
    with_cassandra: bool,
    with_scylla: bool,
    with_dynamo: bool,
    with_cosmos: bool,
    with_elasticsearch: bool,
    with_meilisearch: bool,
    with_typesense: bool,
    with_email: bool,
    with_slack: bool,
    with_datadog: bool,
    with_telemetry: bool,
    with_payments: bool,
    with_rabbitmq: bool,
    with_sqs: bool,
    with_celery: bool,
    with_analytics: bool,
    with_vault: bool,
    with_aws_secrets: bool,
    with_feature_flags: bool,
    with_s3: bool,
    with_gcs: bool,
    with_azure_blob: bool,
    with_llm: bool,
    with_pinecone: bool,
    with_qdrant: bool,
    with_identity: bool,
):
    """
    Generate a new project from the template.

    Non-interactive variant suitable for scripts and CI.
    For an interactive multi-step wizard, use the ``init`` command.
    """
    click.echo()
    click.secho("╔══════════════════════════════════════════════════════════════╗", fg="cyan")
    click.secho("║                                                              ║", fg="cyan")
    click.secho("║   ███████╗ █████╗ ███████╗████████╗███╗   ███╗██╗   ██╗ ██████╗║", fg="cyan")
    click.secho("║   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝████╗ ████║██║   ██║██╔════╝║", fg="cyan")
    click.secho("║   █████╗  ███████║███████╗   ██║   ██╔████╔██║██║   ██║██║     ║", fg="cyan")
    click.secho("║   ██╔══╝  ██╔══██║╚════██║   ██║   ██║╚██╔╝██║╚██╗ ██╔╝██║     ║", fg="cyan")
    click.secho("║   ██║     ██║  ██║███████║   ██║   ██║ ╚═╝ ██║ ╚████╔╝ ╚██████╗║", fg="cyan")
    click.secho("║   ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝  ╚═══╝   ╚═════╝║", fg="cyan")
    click.secho("║                                                              ║", fg="cyan")
    click.secho("║          Production-grade MVC Framework for FastAPI          ║", fg="cyan")
    click.secho("╚══════════════════════════════════════════════════════════════╝", fg="cyan")
    click.echo()

    # Validate project name
    if not project_name.replace("_", "").replace("-", "").isalnum():
        click.secho(
            f"✗ Invalid project name: '{project_name}'. "
            "Use only letters, numbers, underscores, and hyphens.",
            fg="red"
        )
        sys.exit(1)

    # Create generator and run
    generator = ProjectGenerator(
        project_name=project_name,
        output_dir=output_dir,
        init_git=git,
        create_venv=venv,
        install_deps=install,
    )

    # Configure optional backends for env and config pruning
    generator.use_redis = with_redis
    generator.use_mongo = with_mongo
    generator.use_cassandra = with_cassandra
    generator.use_scylla = with_scylla
    generator.use_dynamo = with_dynamo
    generator.use_cosmos = with_cosmos
    generator.use_elasticsearch = with_elasticsearch
    generator.use_meilisearch = with_meilisearch
    generator.use_typesense = with_typesense
    generator.use_email = with_email
    generator.use_slack = with_slack
    generator.use_datadog = with_datadog
    generator.use_telemetry = with_telemetry
    generator.use_payments = with_payments
    generator.use_rabbitmq = with_rabbitmq
    generator.use_sqs = with_sqs
    generator.use_celery = with_celery
    generator.use_analytics = with_analytics
    generator.use_vault = with_vault
    generator.use_aws_secrets = with_aws_secrets
    generator.use_feature_flags = with_feature_flags
    generator.use_s3 = with_s3
    generator.use_gcs = with_gcs
    generator.use_azure_blob = with_azure_blob
    generator.use_llm = with_llm
    generator.use_pinecone = with_pinecone
    generator.use_qdrant = with_qdrant
    generator.use_identity = with_identity

    # Simple helpers for repo files
    def _write_license(path: Path, license_key: str, project: str) -> None:
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

    def _write_contributing(path: Path) -> None:
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

    def _write_codeowners(path: Path, owner: str) -> None:
        if owner:
            path.write_text(f"* {owner}\n")

    def _write_pyproject(path: Path,
                         use_ruff: bool,
                         use_black: bool,
                         use_isort: bool,
                         use_mypy: bool) -> None:
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

    def _write_precommit(path: Path,
                         use_ruff: bool,
                         use_black: bool,
                         use_isort: bool,
                         use_mypy: bool) -> None:
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
        # Local pytest hook
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

    def _write_ci_workflow(path: Path,
                           use_ruff: bool,
                           use_black: bool,
                           use_isort: bool,
                           use_mypy: bool) -> None:
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

    # Collect license / ownership details
    license_key = click.prompt(
        "  License",
        type=click.Choice(["mit", "apache-2.0", "gpl-3.0", "proprietary"], case_sensitive=False),
        default="mit",
    ).lower()
    code_owner = click.prompt(
        "  CODEOWNERS handle/email (optional)",
        default="",
        show_default=False,
    ).strip()

    try:
        # If target directory already exists, ask whether to overwrite
        if generator.project_path.exists():
            click.secho(
                f"Directory '{generator.project_path}' already exists.",
                fg="yellow",
            )
            if not click.confirm(
                "Do you want to overwrite it? This will DELETE existing contents.",
                default=False,
            ):
                click.secho("Aborting project generation.", fg="red")
                sys.exit(1)
            shutil.rmtree(generator.project_path)

        generator.generate()

        # Create concrete .env from generated .env.example using wizard values
        env_example = generator.project_path / ".env.example"
        env_file = generator.project_path / ".env"
        if env_example.exists():
            shutil.copy2(env_example, env_file)
        click.echo()
        click.secho("✓ Project generated successfully!", fg="green", bold=True)
        click.echo()
        click.secho("Next steps:", fg="yellow", bold=True)
        click.echo()
        click.echo(f"  1. cd {project_name}")
        click.echo("  2. pip install -r requirements.txt")
        click.echo("  3. cp .env.example .env  # Configure your environment")
        click.echo("  4. docker-compose up -d  # Start PostgreSQL and Redis (optional)")
        click.echo("  5. python -m uvicorn app:app --reload")
        click.echo()
        click.secho("  → Your API will be available at http://localhost:8000", fg="cyan")
        click.secho("  → API docs at http://localhost:8000/docs", fg="cyan")
        click.echo()
    except Exception as e:
        click.secho(f"✗ Error generating project: {e}", fg="red")
        sys.exit(1)


@cli.command()
def init():
    """
    Interactive, multi-step project initializer with a TUI-style wizard.

    Guides you through project name, output directory, git, virtualenv,
    and dependency installation options, then generates the project.
    """
    # Clear screen for a simple CLI "GUI"
    click.clear()
    click.secho("┌─────────────────────────────────────────────┐", fg="cyan")
    click.secho("│        Project Setup Wizard (CLI UI)       │", fg="cyan")
    click.secho("└─────────────────────────────────────────────┘", fg="cyan")
    click.echo()

    # Step 1: basic info
    click.secho("[1/4] Project details", fg="yellow", bold=True)
    project_name = click.prompt("  Project name", type=str)
    output_dir = click.prompt("  Output directory", default=".", type=str)
    click.echo()

    # Step 2: stack & presets
    click.secho("[2/4] Stack, presets & features", fg="yellow", bold=True)
    api_preset = click.prompt(
        "  API preset",
        type=click.Choice(["auth_only", "crud", "admin"], case_sensitive=False),
        default="crud",
    )
    db_backend = click.prompt(
        "  Database backend",
        type=click.Choice(["postgres", "mysql", "sqlite"], case_sensitive=False),
        default="postgres",
    )
    use_redis = click.confirm("  Use Redis?", default=True)
    use_mongo = click.confirm("  Use MongoDB?", default=False)
    use_cassandra = click.confirm("  Use Cassandra?", default=False)
    use_dynamo = click.confirm("  Use AWS DynamoDB?", default=False)
    use_cosmos = click.confirm("  Use Azure Cosmos DB?", default=False)
    use_scylla = click.confirm("  Use ScyllaDB?", default=False)
    use_elasticsearch = click.confirm("  Use Elasticsearch?", default=False)
    use_email = click.confirm("  Use Email (SMTP/SendGrid)?", default=False)
    use_slack = click.confirm("  Use Slack?", default=False)
    use_datadog = click.confirm("  Use Datadog APM?", default=False)
    use_telemetry = click.confirm("  Use OpenTelemetry (OTel)?", default=False)
    use_payments = click.confirm("  Use Payments (Stripe/Razorpay/PayPal/PayU/Link)?", default=False)
    use_rabbitmq = click.confirm("  Use RabbitMQ for queues?", default=False)
    use_sqs = click.confirm("  Use Amazon SQS for queues?", default=False)
    use_celery = click.confirm("  Use Celery for background jobs?", default=False)
    use_s3 = click.confirm("  Use AWS S3 for file storage?", default=False)
    use_gcs = click.confirm("  Use Google Cloud Storage for file storage?", default=False)
    use_azure_blob = click.confirm("  Use Azure Blob Storage for file storage?", default=False)
    use_meilisearch = click.confirm("  Use Meilisearch for search?", default=False)
    use_typesense = click.confirm("  Use Typesense for search?", default=False)
    use_analytics = click.confirm("  Use analytics / event tracking helpers?", default=False)
    use_vault = click.confirm("  Use HashiCorp Vault for secrets?", default=False)
    use_aws_secrets = click.confirm("  Use AWS Secrets Manager for secrets?", default=False)
    use_feature_flags = click.confirm("  Use feature flags (LaunchDarkly/Unleash)?", default=False)
    use_identity = click.confirm("  Use Identity providers / SSO (Google/GitHub/AzureAD/Okta/Auth0/SAML)?", default=False)
    click.echo()

    # Feature toggles and layout
    enable_auth = click.confirm("  Include auth module?", default=True)
    enable_user_mgmt = click.confirm("  Include user management?", default=True)
    enable_product_crud = click.confirm("  Include example Product CRUD?", default=True)
    layout = click.prompt(
        "  Project layout",
        type=click.Choice(["monolith", "backend-only", "backend+worker"], case_sensitive=False),
        default="monolith",
    )
    enable_alembic = click.confirm("  Include Alembic migrations?", default=True)
    click.echo()

    # Step 3: tooling options
    click.secho("[3/4] Tooling options", fg="yellow", bold=True)
    init_git = click.confirm("  Initialize git repository?", default=True)
    create_venv = click.confirm("  Create a virtual environment (venv)?", default=False)
    install_deps = click.confirm(
        "  Install dependencies after generation?", default=False
    )
    remote_url = click.prompt(
        "  Git remote URL (leave blank to skip)",
        default="",
        show_default=False,
    ).strip()
    push_initial = False
    if remote_url and init_git:
        push_initial = click.confirm(
            "  Push initial commit to this remote after generation?", default=False
        )

    # Quality & tooling toggles
    enable_ruff = click.confirm("  Enable ruff (linter)?", default=True)
    enable_black = click.confirm("  Enable black (formatter)?", default=True)
    enable_isort = click.confirm("  Enable isort (imports)?", default=True)
    enable_mypy = click.confirm("  Enable mypy (type checking)?", default=False)
    enable_precommit = click.confirm("  Add pre-commit hooks?", default=True)
    enable_ci = click.confirm("  Add GitHub Actions CI workflow?", default=True)
    click.echo()

    # Step 4: ports, secrets & summary
    click.secho("[4/4] Ports, secrets & review", fg="yellow", bold=True)

    # App port with conflict check
    default_app_port = 8000
    app_port = click.prompt("  Application port", default=default_app_port, type=int)

    def _port_in_use(port: int, host: str = "127.0.0.1") -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            return s.connect_ex((host, port)) == 0

    if _port_in_use(app_port):
        candidate = app_port + 1
        while _port_in_use(candidate) and candidate < app_port + 10:
            candidate += 1
        if not _port_in_use(candidate):
            if click.confirm(
                f"  Port {app_port} is in use. Use {candidate} instead?", default=True
            ):
                app_port = candidate

    # DB connection details (only relevant for non-sqlite)
    db_name = project_name
    db_host = "localhost"
    db_port = 5432 if db_backend == "postgres" else 3306
    if db_backend != "sqlite":
        db_name = click.prompt("  Database name", default=project_name, type=str)
        db_host = click.prompt("  Database host", default="localhost", type=str)
        db_port = click.prompt(
            "  Database port",
            default=5432 if db_backend == "postgres" else 3306,
            type=int,
        )

    # Secrets and CORS
    auto_secrets = click.confirm(
        "  Auto-generate JWT secret & bcrypt salt?", default=True
    )
    jwt_secret = None
    bcrypt_salt = None

    if auto_secrets:
        jwt_secret = secrets.token_urlsafe(32)
        try:
            import bcrypt  # type: ignore

            bcrypt_salt = bcrypt.gensalt().decode("utf-8")
        except Exception:
            raw = base64.b64encode(os.urandom(16)).decode("utf-8")
            bcrypt_salt = f"$2b$12${raw[:22]}"

    cors_origins = click.prompt(
        "  CORS origins (comma-separated)",
        default="http://localhost:3000,http://localhost:8000",
        type=str,
    )

    click.echo()
    # Summary + confirmation
    click.secho("Review configuration", fg="yellow", bold=True)
    click.echo(f"  Project name : {project_name}")
    click.echo(f"  Output dir   : {Path(output_dir).resolve()}")
    click.echo(f"  Git init     : {'yes' if init_git else 'no'}")
    click.echo(f"  Virtualenv   : {'yes' if create_venv else 'no'}")
    click.echo(f"  Install deps : {'yes' if install_deps else 'no'}")
    click.echo(f"  API preset   : {api_preset}")
    click.echo(f"  DB backend   : {db_backend}")
    click.echo(f"  Use Redis    : {'yes' if use_redis else 'no'}")
    click.echo(f"  Features     : auth={enable_auth}, users={enable_user_mgmt}, product_crud={enable_product_crud}")
    click.echo(f"  Layout       : {layout}")
    click.echo(f"  Alembic      : {'yes' if enable_alembic else 'no'}")
    click.echo(f"  App port     : {app_port}")
    if db_backend != "sqlite":
        click.echo(f"  DB host      : {db_host}")
        click.echo(f"  DB port      : {db_port}")
        click.echo(f"  DB name      : {db_name}")
    click.echo()

    if not click.confirm("Proceed with project creation?", default=True):
        click.secho("Aborting project generation.", fg="red")
        sys.exit(1)

    # Reuse the same generator used by the non-interactive command
    generator = ProjectGenerator(
        project_name=project_name,
        output_dir=output_dir,
        init_git=init_git,
        create_venv=create_venv,
        install_deps=install_deps,
    )

    # Attach preset / env options so _create_env_example can use them
    generator.api_preset = api_preset
    generator.db_backend = db_backend
    generator.use_redis = use_redis
    generator.use_mongo = use_mongo
    generator.use_cassandra = use_cassandra
    generator.use_dynamo = use_dynamo
    generator.use_cosmos = use_cosmos
    generator.use_scylla = use_scylla
    generator.use_elasticsearch = use_elasticsearch
    generator.use_email = use_email
    generator.use_slack = use_slack
    generator.use_datadog = use_datadog
    generator.use_telemetry = use_telemetry
    generator.use_payments = use_payments
    generator.use_rabbitmq = use_rabbitmq
    generator.use_sqs = use_sqs
    generator.use_celery = use_celery
    generator.use_s3 = use_s3
    generator.use_gcs = use_gcs
    generator.use_azure_blob = use_azure_blob
    generator.use_meilisearch = use_meilisearch
    generator.use_typesense = use_typesense
    generator.use_analytics = use_analytics
    generator.use_vault = use_vault
    generator.use_aws_secrets = use_aws_secrets
    generator.use_feature_flags = use_feature_flags
    generator.use_identity = use_identity
    generator.app_port = app_port
    generator.db_name = db_name
    generator.db_host = db_host
    generator.db_port = str(db_port)
    generator.jwt_secret = jwt_secret
    generator.bcrypt_salt = bcrypt_salt
    generator.cors_origins = cors_origins
    generator.enable_auth = enable_auth
    generator.enable_user_mgmt = enable_user_mgmt
    generator.enable_product_crud = enable_product_crud
    generator.layout = layout
    generator.enable_alembic = enable_alembic
    generator.enable_ruff = enable_ruff
    generator.enable_black = enable_black
    generator.enable_isort = enable_isort
    generator.enable_mypy = enable_mypy
    generator.enable_precommit = enable_precommit
    generator.enable_ci = enable_ci
    # runtime helpers enabled by default; could be toggled later
    generator.enable_runtime_helpers = True

    try:
        # If target directory already exists, ask whether to overwrite
        if generator.project_path.exists():
            click.secho(
                f"Directory '{generator.project_path}' already exists.",
                fg="yellow",
            )
            if not click.confirm(
                "Do you want to overwrite it? This will DELETE existing contents.",
                default=False,
            ):
                click.secho("Aborting project generation.", fg="red")
                sys.exit(1)
            shutil.rmtree(generator.project_path)

        generator.generate()

        # Create concrete .env from example using wizard values
        env_example = generator.project_path / ".env.example"
        env_file = generator.project_path / ".env"
        if env_example.exists():
            shutil.copy2(env_example, env_file)

        # Write / override LICENSE, CONTRIBUTING.md, CODEOWNERS
        _write_license(generator.project_path / "LICENSE", license_key, project_name)
        _write_contributing(generator.project_path / "CONTRIBUTING.md")
        if code_owner:
            _write_codeowners(generator.project_path / "CODEOWNERS", code_owner)

        # Write quality/tooling configs
        if generator.enable_ruff or generator.enable_black or generator.enable_isort or generator.enable_mypy:
            _write_pyproject(
                generator.project_path / "pyproject.toml",
                generator.enable_ruff,
                generator.enable_black,
                generator.enable_isort,
                generator.enable_mypy,
            )
        if generator.enable_precommit:
            _write_precommit(
                generator.project_path / ".pre-commit-config.yaml",
                generator.enable_ruff,
                generator.enable_black,
                generator.enable_isort,
                generator.enable_mypy,
            )
        if generator.enable_ci:
            ci_dir = generator.project_path / ".github" / "workflows"
            ci_dir.mkdir(parents=True, exist_ok=True)
            _write_ci_workflow(
                ci_dir / "ci.yml",
                generator.enable_ruff,
                generator.enable_black,
                generator.enable_isort,
                generator.enable_mypy,
            )

        # Configure git remote and optional first push
        if init_git and remote_url:
            try:
                subprocess.run(
                    ["git", "remote", "add", "origin", remote_url],
                    cwd=generator.project_path,
                    check=False,
                    capture_output=True,
                )
                if push_initial:
                    subprocess.run(
                        ["git", "push", "-u", "origin", "HEAD"],
                        cwd=generator.project_path,
                        check=False,
                    )
            except Exception:
                # Best-effort; failures are non-fatal for project generation
                pass

        click.echo()
        click.secho("✓ Project generated successfully!", fg="green", bold=True)
        click.echo()
        click.secho("Summary:", fg="yellow", bold=True)
        click.echo(f"  Project name: {project_name}")
        click.echo(f"  Location:     {generator.project_path}")
        click.echo(f"  Git init:     {'yes' if init_git else 'no'}")
        click.echo(f"  Virtualenv:   {'yes' if create_venv else 'no'}")
        click.echo(f"  Install deps: {'yes' if install_deps else 'no'}")
        click.echo()
    except Exception as e:
        click.secho(f"✗ Error generating project: {e}", fg="red")
        sys.exit(1)


# ============================================================================
# ADD COMMAND GROUP
# ============================================================================

@cli.group()
def add():
    """
    Add components to an existing FastMVC project.

    \b
    Available subcommands:
        entity - Generate a new entity with full CRUD

    \b
    Examples:
        $ fastmvc add entity Product
        $ fastmvc add entity Order --no-tests
    """
    pass


@add.command("entity")
@click.argument("entity_name")
@click.option(
    "--tests/--no-tests",
    default=True,
    help="Generate test files (default: True)"
)
def add_entity(entity_name: str, tests: bool):
    """
    Generate a new entity with full CRUD scaffolding.

    Creates model, repository, service, controller, DTOs, dependencies,
    and tests for the specified entity.

    \b
    Arguments:
        ENTITY_NAME: Name of the entity in PascalCase (e.g., Product, Order)

    \b
    Examples:
        $ fastmvc add entity Product
        $ fastmvc add entity OrderItem --no-tests

    \b
    Generated files:
        • models/<entity>.py
        • repositories/<entity>.py
        • services/<entity>/
        • controllers/<entity>/
        • dtos/requests/<entity>/
        • dependencies/repositiories/<entity>.py
        • tests/unit/models/test_<entity>.py
    """
    click.echo()
    click.secho(f"→ Generating entity: {entity_name}", fg="blue", bold=True)
    click.echo()

    # Validate entity name
    if not entity_name[0].isupper():
        click.secho(
            f"✗ Entity name should be in PascalCase (e.g., Product, not {entity_name})",
            fg="yellow"
        )
        entity_name = entity_name[0].upper() + entity_name[1:]
        click.secho(f"  Using: {entity_name}", fg="white")

    # Check we're in a FastMVC project
    project_path = Path.cwd()
    if not (project_path / "app.py").exists():
        click.secho(
            "✗ Not in a FastMVC project directory. "
            "Run this command from your project root.",
            fg="red"
        )
        sys.exit(1)

    try:
        generator = EntityGenerator(
            entity_name=entity_name,
            project_path=project_path,
            with_tests=tests,
        )
        generator.generate()

        click.echo()
        click.secho("✓ Entity generated successfully!", fg="green", bold=True)
        click.echo()
        click.secho("Next steps:", fg="yellow", bold=True)
        click.echo()
        click.echo("  1. Review generated files in models/, services/, controllers/")
        click.echo("  2. Register the router in app.py:")
        click.echo()
        click.secho(f"     from controllers.{entity_name.lower()} import router as {entity_name.lower()}_router", fg="white", dim=True)
        click.secho(f"     app.include_router({entity_name.lower()}_router)", fg="white", dim=True)
        click.echo()
        click.echo(f"  3. Generate migration: fastmvc migrate generate 'add_{entity_name.lower()}_table'")
        click.echo("  4. Apply migration: fastmvc migrate upgrade")
        click.echo()
    except Exception as e:
        click.secho(f"✗ Error generating entity: {e}", fg="red")
        sys.exit(1)


@add.command("service")
@click.argument(
    "service_name",
    type=click.Choice(
        [
            "mongo",
            "cassandra",
            "scylla",
            "dynamo",
            "cosmos",
            "elasticsearch",
            "email",
            "slack",
            "datadog",
            "telemetry",
            "payments",
            "identity",
            "queues",
            "jobs",
            "storage",
        ],
        case_sensitive=False,
    ),
)
def add_service(service_name: str):
    """
    Add an infrastructure service integration to an existing FastMVC project.

    This command copies the relevant config/ and DTO/configuration modules
    from the FastMVC template into the current project without overwriting
    existing files, so the server keeps working after the addition.

    \b
    Examples:
        $ fastmvc add service email
        $ fastmvc add service mongo
        $ fastmvc add service elasticsearch
    """
    click.echo()
    click.secho(f"→ Adding service integration: {service_name}", fg="blue", bold=True)
    click.echo()

    project_path = Path.cwd()
    if not (project_path / "app.py").exists():
        click.secho(
            "✗ Not in a FastMVC project directory. "
            "Run this command from your project root.",
            fg="red",
        )
        sys.exit(1)

    # Resolve template root using ProjectGenerator helper
    try:
        template_root = ProjectGenerator("tmp")._get_template_path()
    except Exception as e:  # pragma: no cover - defensive
        click.secho(f"✗ Could not locate FastMVC template: {e}", fg="red")
        sys.exit(1)

    def _copy_dir(rel: str) -> None:
        src = template_root / rel
        dst = project_path / rel
        if not src.exists():
            return
        if dst.exists():
            click.secho(f"  • Skipping existing directory: {rel}", fg="yellow")
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
        click.secho(f"  ✓ Added directory: {rel}", fg="green")

    def _copy_file(rel: str) -> None:
        src = template_root / rel
        dst = project_path / rel
        if not src.exists():
            return
        if dst.exists():
            click.secho(f"  • Skipping existing file: {rel}", fg="yellow")
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        click.secho(f"  ✓ Added file: {rel}", fg="green")

    service_name = service_name.lower()

    if service_name in {
        "mongo",
        "cassandra",
        "scylla",
        "dynamo",
        "cosmos",
        "elasticsearch",
        "slack",
        "datadog",
        "telemetry",
        "payments",
    }:
        _copy_dir(f"config/{service_name}")
        _copy_file(f"configurations/{service_name}.py")
        _copy_file(f"dtos/configurations/{service_name}.py")
    elif service_name == "identity":
        _copy_dir("config/identity")
        _copy_file("configurations/identity.py")
        _copy_dir("dtos/configurations/identity")
        _copy_dir("services/auth")
    elif service_name == "queues":
        _copy_dir("config/queues")
        _copy_file("configurations/queues.py")
        _copy_file("dtos/configurations/queues.py")
        _copy_dir("services/queues")
    elif service_name == "jobs":
        _copy_dir("config/jobs")
        _copy_file("configurations/jobs.py")
        _copy_file("dtos/configurations/jobs.py")
        _copy_dir("services/jobs")
    elif service_name == "storage":
        _copy_dir("config/storage")
        _copy_file("configurations/storage.py")
        _copy_file("dtos/configurations/storage.py")
        _copy_dir("services/storage")
    elif service_name == "email":
        _copy_dir("config/email")
        _copy_file("configurations/email.py")
        _copy_file("dtos/configurations/email.py")
        _copy_dir("services/communications")
    else:  # pragma: no cover - guarded by click.Choice
        click.secho(f"✗ Unsupported service: {service_name}", fg="red")
        sys.exit(1)

    click.echo()
    click.secho("✓ Service integration files added.", fg="green", bold=True)
    click.echo("  → Update the corresponding config/*/config.json to enable the service.")
    click.echo("  → No changes were made to app startup, so the server will continue to run.")
    click.echo()


# ============================================================================
# MIGRATE COMMAND GROUP
# ============================================================================

@cli.group()
def migrate():
    """
    Database migration commands using Alembic.

    \b
    Available subcommands:
        generate - Create a new migration
        upgrade  - Apply migrations
        downgrade - Rollback migrations
        status   - Show current migration status
        history  - Show migration history

    \b
    Examples:
        $ fastmvc migrate generate "add users table"
        $ fastmvc migrate upgrade
        $ fastmvc migrate downgrade -1
    """
    pass


@migrate.command("generate")
@click.argument("message")
@click.option(
    "--autogenerate/--no-autogenerate",
    default=True,
    help="Auto-generate migration from model changes (default: True)"
)
def migrate_generate(message: str, autogenerate: bool):
    """
    Generate a new database migration.

    Creates a new migration file based on changes to your SQLAlchemy models.

    \b
    Arguments:
        MESSAGE: Description of the migration (e.g., "add products table")

    \b
    Examples:
        $ fastmvc migrate generate "add products table"
        $ fastmvc migrate generate "add email index" --no-autogenerate
    """
    click.secho(f"→ Generating migration: {message}", fg="blue")

    # Check for alembic.ini
    if not Path("alembic.ini").exists():
        click.secho("✗ alembic.ini not found. Are you in a FastMVC project?", fg="red")
        sys.exit(1)

    try:
        cmd = ["alembic", "revision"]
        if autogenerate:
            cmd.append("--autogenerate")
        cmd.extend(["-m", message])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            click.secho("✓ Migration generated successfully!", fg="green")
            click.echo(result.stdout)
        else:
            click.secho("✗ Migration generation failed:", fg="red")
            click.echo(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


@migrate.command("upgrade")
@click.argument("revision", default="head")
def migrate_upgrade(revision: str):
    """
    Apply database migrations.

    \b
    Arguments:
        REVISION: Target revision (default: "head" for latest)

    \b
    Examples:
        $ fastmvc migrate upgrade        # Apply all pending migrations
        $ fastmvc migrate upgrade head   # Same as above
        $ fastmvc migrate upgrade +1     # Apply next migration
    """
    click.secho(f"→ Upgrading database to: {revision}", fg="blue")

    try:
        result = subprocess.run(
            ["alembic", "upgrade", revision],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.secho("✓ Database upgraded successfully!", fg="green")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.secho("✗ Upgrade failed:", fg="red")
            click.echo(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


@migrate.command("downgrade")
@click.argument("revision", default="-1")
def migrate_downgrade(revision: str):
    """
    Rollback database migrations.

    \b
    Arguments:
        REVISION: Target revision (default: "-1" for previous)

    \b
    Examples:
        $ fastmvc migrate downgrade      # Rollback one migration
        $ fastmvc migrate downgrade -1   # Same as above
        $ fastmvc migrate downgrade base # Rollback all migrations
    """
    click.secho(f"→ Downgrading database to: {revision}", fg="yellow")

    try:
        result = subprocess.run(
            ["alembic", "downgrade", revision],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.secho("✓ Database downgraded successfully!", fg="green")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.secho("✗ Downgrade failed:", fg="red")
            click.echo(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


@migrate.command("status")
def migrate_status():
    """
    Show current database migration status.

    Displays the current revision applied to the database.
    """
    click.secho("→ Checking migration status...", fg="blue")

    try:
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.secho("Current revision:", fg="cyan", bold=True)
            click.echo(result.stdout or "  No migrations applied yet")
        else:
            click.echo(result.stderr)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


@migrate.command("history")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def migrate_history(verbose: bool):
    """
    Show migration history.

    Displays all available migrations and their status.
    """
    click.secho("→ Migration history:", fg="blue")

    try:
        cmd = ["alembic", "history"]
        if verbose:
            cmd.append("--verbose")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            click.echo(result.stdout or "  No migrations found")
        else:
            click.echo(result.stderr)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


# ============================================================================
# INFO & VERSION COMMANDS
# ============================================================================

@cli.command()
def info():
    """
    Display information about FastMVC.

    Shows details about the framework including version,
    features, and documentation links.
    """
    click.echo()
    click.secho("╔══════════════════════════════════════════════════════════════╗", fg="cyan")
    click.secho("║                   FastMVC Framework                          ║", fg="cyan")
    click.secho("║          Production-grade MVC for FastAPI                    ║", fg="cyan")
    click.secho("╚══════════════════════════════════════════════════════════════╝", fg="cyan")
    click.echo()
    click.echo(f"  Version:     {__version__}")
    click.echo(f"  Python:      {sys.version.split()[0]}")
    click.echo("  PyPI:        https://pypi.org/project/pyfastmvc/")
    click.echo()
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="white", dim=True)
    click.secho("Core Features:", fg="yellow", bold=True)
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="white", dim=True)
    click.echo("  🏗️  MVC Architecture Pattern")
    click.echo("  🔐 Built-in JWT Authentication")
    click.echo("  🛡️  90+ Production Middlewares (fastmiddleware)")
    click.echo("  ⚡ Rate Limiting (Sliding Window)")
    click.echo("  📊 Request Context & Timing")
    click.echo("  ✅ Comprehensive Validation")
    click.echo("  🧪 Full Test Suite")
    click.echo()
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="white", dim=True)
    click.secho("Middleware Stack (fastmiddleware):", fg="green", bold=True)
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="white", dim=True)
    click.echo("  → RequestContextMiddleware  - Request tracking & URN")
    click.echo("  → TimingMiddleware          - Response time headers")
    click.echo("  → LoggingMiddleware         - Structured request logs")
    click.echo("  → RateLimitMiddleware       - Rate limiting")
    click.echo("  → SecurityHeadersMiddleware - CSP, HSTS, XSS protection")
    click.echo("  → CORSMiddleware            - Cross-origin requests")
    click.echo()
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="white", dim=True)
    click.secho("Project Structure:", fg="yellow", bold=True)
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="white", dim=True)
    click.echo("  📋 abstractions/   → Base interfaces & contracts")
    click.echo("  🎮 controllers/    → HTTP route handlers")
    click.echo("  🔧 services/       → Business logic layer")
    click.echo("  🗄️  repositories/   → Data access layer")
    click.echo("  📊 models/         → SQLAlchemy ORM models")
    click.echo("  📨 dtos/           → Data transfer objects")
    click.echo("  🛡️  middlewares/    → Request processing")
    click.echo("  🔄 migrations/     → Alembic migrations")
    click.echo("  🧪 tests/          → Test suite")
    click.echo()
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="white", dim=True)
    click.secho("CLI Commands:", fg="cyan", bold=True)
    click.secho("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="white", dim=True)
    click.echo("  fastmvc generate <name>          → Create new project")
    click.echo("  fastmvc add entity <name>        → Add CRUD entity")
    click.echo("  fastmvc migrate generate <msg>   → Create migration")
    click.echo("  fastmvc migrate upgrade          → Apply migrations")
    click.echo("  fastmvc migrate downgrade        → Rollback migrations")
    click.echo("  fastmvc migrate status           → Show current status")
    click.echo("  fastmvc version                  → Show version")
    click.echo()


@cli.command()
def version():
    """Display the FastMVC version."""
    click.echo(f"FastMVC v{__version__}")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
