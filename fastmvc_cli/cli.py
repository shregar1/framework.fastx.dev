"""
FastMVC CLI - Command Line Interface.

This module provides the main CLI entry point for FastMVC framework.
It uses Click for building the command-line interface.

Commands:
    generate: Create a new FastMVC project from template
    add: Add entities, migrations, etc. to existing project
    migrate: Database migration commands
    version: Display the current FastMVC version (optional PyPI check)
    lint: Ruff and optional mypy for the project tree
    run: pre_run hooks then uvicorn
    info: Display information about FastMVC

Example:
    $ fastmvc generate my_api
    $ fastmvc add entity Product
    $ fastmvc migrate upgrade
    $ fastmvc version
    $ fastmvc lint
    $ fastmvc run
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
from typing import Optional

import click

from fastmvc_cli import __version__
from fastmvc_cli.alembic_utils import alembic_base_args, alembic_cwd, find_alembic_ini
from fastmvc_cli.doctor import export_openapi_json, run_doctor
from fastmvc_cli.entity_generator import EntityGenerator
from fastmvc_cli.generator import ProjectGenerator
from fastmvc_cli.hooks import run_post_generate, run_pre_run
from fastmvc_cli.init_ci import run_init_ci
from fastmvc_cli.presets import apply_template_pack
from fastmvc_cli.scaffold_helpers import (
    write_ci_workflow,
    write_codeowners,
    write_contributing,
    write_license,
    write_precommit,
    write_pyproject,
)


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
    "--with-neo4j/--no-neo4j",
    default=False,
    help="Include Neo4j graph database configuration and helpers (default: False)",
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
    "--with-service-bus/--no-service-bus",
    default=False,
    help="Include Azure Service Bus queue configuration and helpers (default: False)",
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
    "--with-events/--no-events",
    default=False,
    help="Include cloud event bus configuration (SNS/EventBridge/Event Hubs/Kafka) (default: False)",
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
@click.option(
    "--with-streams/--no-streams",
    default=False,
    help="Include market/event streams hub configuration and helpers (default: False)",
)
@click.option(
    "--template-pack",
    type=click.Choice(["minimal", "standard", "full"], case_sensitive=False),
    default="standard",
    help="Preset: minimal (lean API), standard (defaults), full (auth, jobs, queues, analytics, …).",
)
@click.option(
    "--with-docker-compose/--no-docker-compose",
    default=True,
    help="Include docker-compose.yml and Dockerfile for Postgres + Redis (default: on).",
)
@click.option(
    "--export-openapi/--no-export-openapi",
    default=False,
    help="After generation, write openapi.json (requires dependencies; use --install).",
)
@click.option(
    "--ci",
    is_flag=True,
    help="Non-interactive: default license, skip prompts (use with --force to overwrite).",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing project directory without confirmation.",
)
@click.option(
    "--spdx-license",
    default=None,
    help="License when using --ci (default: mit).",
)
@click.option(
    "--code-owner",
    default="",
    show_default=False,
    help="CODEOWNERS line when using --ci.",
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
    with_neo4j: bool,
    with_meilisearch: bool,
    with_typesense: bool,
    with_email: bool,
    with_slack: bool,
    with_datadog: bool,
    with_telemetry: bool,
    with_payments: bool,
    with_rabbitmq: bool,
    with_sqs: bool,
    with_service_bus: bool,
    with_celery: bool,
    with_analytics: bool,
    with_events: bool,
    with_vault: bool,
    with_aws_secrets: bool,
    with_feature_flags: bool,
    with_s3: bool,
    with_gcs: bool,
    with_azure_blob: bool,
    with_llm: bool,
    with_pinecone: bool,
    with_qdrant: bool,
    with_streams: bool,
    with_identity: bool,
    template_pack: str,
    with_docker_compose: bool,
    export_openapi: bool,
    ci: bool,
    force: bool,
    spdx_license: Optional[str],
    code_owner: str,
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
    generator.use_neo4j = with_neo4j
    generator.use_meilisearch = with_meilisearch
    generator.use_typesense = with_typesense
    generator.use_email = with_email
    generator.use_slack = with_slack
    generator.use_datadog = with_datadog
    generator.use_telemetry = with_telemetry
    generator.use_payments = with_payments
    generator.use_rabbitmq = with_rabbitmq
    generator.use_sqs = with_sqs
    generator.use_service_bus = with_service_bus
    generator.use_celery = with_celery
    generator.use_analytics = with_analytics
    generator.use_events = with_events
    generator.use_vault = with_vault
    generator.use_aws_secrets = with_aws_secrets
    generator.use_feature_flags = with_feature_flags
    generator.use_s3 = with_s3
    generator.use_gcs = with_gcs
    generator.use_azure_blob = with_azure_blob
    generator.use_llm = with_llm
    generator.use_pinecone = with_pinecone
    generator.use_qdrant = with_qdrant
    generator.use_streams = with_streams
    generator.use_identity = with_identity

    generator.include_docker_compose = with_docker_compose
    try:
        apply_template_pack(generator, template_pack)
    except ValueError as e:
        click.secho(str(e), fg="red")
        sys.exit(1)

    # Collect license / ownership details
    if ci:
        license_key = (spdx_license or "mit").lower()
        code_owner = (code_owner or "").strip()
    else:
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
            if not force:
                if ci:
                    click.secho("Aborting: pass --force to overwrite.", fg="red")
                    sys.exit(1)
                if not click.confirm(
                    "Do you want to overwrite it? This will DELETE existing contents.",
                    default=False,
                ):
                    click.secho("Aborting project generation.", fg="red")
                    sys.exit(1)
            shutil.rmtree(generator.project_path)

        generator.generate()

        write_license(generator.project_path / "LICENSE", license_key, project_name)
        write_contributing(generator.project_path / "CONTRIBUTING.md")
        if code_owner:
            write_codeowners(generator.project_path / "CODEOWNERS", code_owner)
        try:
            run_post_generate(generator.project_path)
        except subprocess.CalledProcessError as e:
            click.secho(f"  ✗ post_generate hook failed (exit {e.returncode})", fg="red")
            sys.exit(1)

        if export_openapi:
            ok, msg = export_openapi_json(generator.project_path)
            if ok:
                click.secho(f"  ✓ OpenAPI schema written: {msg}", fg="green")
            else:
                click.secho(f"  ⚠ OpenAPI export skipped: {msg}", fg="yellow")

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
        step = 1
        click.echo(f"  {step}. cd {project_name}")
        step += 1
        if venv:
            if sys.platform == "win32":
                click.echo(f"  {step}. .venv\\Scripts\\activate")
            else:
                click.echo(f"  {step}. source .venv/bin/activate")
            step += 1
        if not install:
            click.echo(f"  {step}. pip install -r requirements.txt")
            step += 1
        click.echo(f"  {step}. cp .env.example .env  # Configure your environment")
        step += 1
        click.echo(f"  {step}. docker-compose up -d  # Start PostgreSQL and Redis (optional)")
        step += 1
        click.echo(f"  {step}. python -m uvicorn app:app --reload")
        click.echo()
        click.secho("  → Your API will be available at http://localhost:8000", fg="cyan")
        click.secho("  → API docs at http://localhost:8000/docs", fg="cyan")
        click.echo()
    except Exception as e:
        click.secho(f"✗ Error generating project: {e}", fg="red")
        sys.exit(1)


@cli.command()
@click.argument("project_name", required=False)
@click.option(
    "--ci",
    is_flag=True,
    help="Non-interactive CI defaults (requires PROJECT_NAME). Use -o for output dir.",
)
@click.option(
    "-o",
    "--output-dir",
    default=".",
    show_default=True,
    help="Output directory for generated project.",
)
@click.option(
    "--force",
    is_flag=True,
    help="With --ci: overwrite existing project directory without prompt.",
)
def init(project_name: Optional[str], ci: bool, output_dir: str, force: bool):
    """
    Interactive, multi-step project initializer with a TUI-style wizard.

    Guides you through project name, output directory, git, virtualenv,
    and dependency installation options, then generates the project.

    Use ``--ci PROJECT_NAME`` for a non-interactive standard stack (CI / automation).
    """
    if ci:
        if not project_name:
            raise click.UsageError("Usage: fastmvc init --ci PROJECT_NAME [-o DIR] [--force]")
        run_init_ci(project_name, output_dir, force=force)
        return

    # Clear screen for a simple CLI "GUI"
    click.clear()
    click.secho("┌─────────────────────────────────────────────┐", fg="cyan")
    click.secho("│        Project Setup Wizard (CLI UI)       │", fg="cyan")
    click.secho("└─────────────────────────────────────────────┘", fg="cyan")
    click.echo()

    # Step 1: basic info
    click.secho("[1/4] Project details", fg="yellow", bold=True)
    project_name = click.prompt(
        "  Project name",
        type=str,
        default=(project_name or "") or None,
    )
    output_dir = click.prompt("  Output directory", default=output_dir or ".", type=str)
    click.echo()

    # Step 2: stack & presets
    click.secho("[2/4] Stack, presets & features", fg="yellow", bold=True)
    template_pack = click.prompt(
        "  Template pack",
        type=click.Choice(["minimal", "standard", "full"], case_sensitive=False),
        default="standard",
    )
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
    use_neo4j = click.confirm("  Use Neo4j graph DB?", default=False)
    use_email = click.confirm("  Use Email (SMTP/SendGrid)?", default=False)
    use_slack = click.confirm("  Use Slack?", default=False)
    use_datadog = click.confirm("  Use Datadog APM?", default=False)
    use_telemetry = click.confirm("  Use OpenTelemetry (OTel)?", default=False)
    use_payments = click.confirm("  Use Payments (Stripe/Razorpay/PayPal/PayU/Link)?", default=False)
    use_rabbitmq = click.confirm("  Use RabbitMQ for queues?", default=False)
    use_sqs = click.confirm("  Use Amazon SQS for queues?", default=False)
    use_service_bus = click.confirm("  Use Azure Service Bus for queues?", default=False)
    use_celery = click.confirm("  Use Celery for background jobs?", default=False)
    use_s3 = click.confirm("  Use AWS S3 for file storage?", default=False)
    use_gcs = click.confirm("  Use Google Cloud Storage for file storage?", default=False)
    use_azure_blob = click.confirm("  Use Azure Blob Storage for file storage?", default=False)
    use_meilisearch = click.confirm("  Use Meilisearch for search?", default=False)
    use_typesense = click.confirm("  Use Typesense for search?", default=False)
    use_analytics = click.confirm("  Use analytics / event tracking helpers?", default=False)
    use_events = click.confirm("  Use cloud event bus (SNS/EventBridge/Event Hubs/Kafka)?", default=False)
    use_vault = click.confirm("  Use HashiCorp Vault for secrets?", default=False)
    use_aws_secrets = click.confirm("  Use AWS Secrets Manager for secrets?", default=False)
    use_feature_flags = click.confirm("  Use feature flags (LaunchDarkly/Unleash)?", default=False)
    use_identity = click.confirm("  Use Identity providers / SSO (Google/GitHub/AzureAD/Okta/Auth0/SAML)?", default=False)
    use_streams = click.confirm("  Use market/event streams hub?", default=False)
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

    include_docker_compose = click.confirm(
        "  Include docker-compose.yml for Postgres + Redis?",
        default=True,
    )
    export_openapi_after = click.confirm(
        "  Write openapi.json after generation (requires dependencies installed)?",
        default=False,
    )

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

    click.echo()
    # Summary + confirmation
    click.secho("Review configuration", fg="yellow", bold=True)
    click.echo(f"  Project name : {project_name}")
    click.echo(f"  Output dir   : {Path(output_dir).resolve()}")
    click.echo(f"  Git init     : {'yes' if init_git else 'no'}")
    click.echo(f"  Virtualenv   : {'yes' if create_venv else 'no'}")
    click.echo(f"  Install deps : {'yes' if install_deps else 'no'}")
    click.echo(f"  Template pack: {template_pack}")
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
    generator.use_neo4j = use_neo4j
    generator.use_email = use_email
    generator.use_slack = use_slack
    generator.use_datadog = use_datadog
    generator.use_telemetry = use_telemetry
    generator.use_payments = use_payments
    generator.use_rabbitmq = use_rabbitmq
    generator.use_sqs = use_sqs
    generator.use_service_bus = use_service_bus
    generator.use_celery = use_celery
    generator.use_s3 = use_s3
    generator.use_gcs = use_gcs
    generator.use_azure_blob = use_azure_blob
    generator.use_meilisearch = use_meilisearch
    generator.use_typesense = use_typesense
    generator.use_analytics = use_analytics
    generator.use_events = use_events
    generator.use_vault = use_vault
    generator.use_aws_secrets = use_aws_secrets
    generator.use_feature_flags = use_feature_flags
    generator.use_identity = use_identity
    generator.use_streams = use_streams
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

    generator.include_docker_compose = include_docker_compose
    if template_pack != "standard":
        if click.confirm(
            f"  Apply '{template_pack}' template pack (overrides feature toggles)?",
            default=True,
        ):
            try:
                apply_template_pack(generator, template_pack)
            except ValueError as e:
                click.secho(str(e), fg="red")
                sys.exit(1)

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

        if export_openapi_after:
            ok, msg = export_openapi_json(generator.project_path)
            if ok:
                click.secho(f"  ✓ OpenAPI schema written: {msg}", fg="green")
            else:
                click.secho(f"  ⚠ OpenAPI export skipped: {msg}", fg="yellow")

        # Create concrete .env from example using wizard values
        env_example = generator.project_path / ".env.example"
        env_file = generator.project_path / ".env"
        if env_example.exists():
            shutil.copy2(env_example, env_file)

        # Write / override LICENSE, CONTRIBUTING.md, CODEOWNERS
        write_license(generator.project_path / "LICENSE", license_key, project_name)
        write_contributing(generator.project_path / "CONTRIBUTING.md")
        if code_owner:
            write_codeowners(generator.project_path / "CODEOWNERS", code_owner)

        try:
            run_post_generate(generator.project_path)
        except subprocess.CalledProcessError as e:
            click.secho(f"✗ post_generate hook failed (exit {e.returncode})", fg="red")
            sys.exit(1)

        # Write quality/tooling configs
        if generator.enable_ruff or generator.enable_black or generator.enable_isort or generator.enable_mypy:
            write_pyproject(
                generator.project_path / "pyproject.toml",
                generator.enable_ruff,
                generator.enable_black,
                generator.enable_isort,
                generator.enable_mypy,
            )
        if generator.enable_precommit:
            write_precommit(
                generator.project_path / ".pre-commit-config.yaml",
                generator.enable_ruff,
                generator.enable_black,
                generator.enable_isort,
                generator.enable_mypy,
            )
        if generator.enable_ci:
            ci_dir = generator.project_path / ".github" / "workflows"
            ci_dir.mkdir(parents=True, exist_ok=True)
            write_ci_workflow(
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
        if create_venv:
            if sys.platform == "win32":
                click.echo("  Activate:     .venv\\Scripts\\activate")
            else:
                click.echo("  Activate:     source .venv/bin/activate")
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


# Single source of truth for add/remove service: dirs, files, and requirements per service.
_REQ = {
    "mongo": ["pymongo>=4.6.0,<5.0.0"],
    "cassandra": ["cassandra-driver>=3.28.0,<4.0.0"],
    "scylla": ["cassandra-driver>=3.28.0,<4.0.0"],
    "dynamo": ["boto3>=1.28.0,<2.0.0"],
    "cosmos": ["azure-cosmos>=4.5.0,<5.0.0"],
    "elasticsearch": ["elasticsearch>=8.0.0,<9.0.0"],
    "graph": ["neo4j>=5.0.0,<6.0.0"],
    "slack": [],
    "datadog": ["ddtrace>=2.0.0,<3.0.0"],
    "telemetry": ["opentelemetry-sdk>=1.23.0,<2.0.0", "opentelemetry-instrumentation-fastapi>=0.44b0,<1.0.0"],
}
SERVICE_SPECS: dict[str, dict] = {
    **{
        s: {
            "dirs": [f"config/{s}"],
            "files": [f"configurations/{s}.py", f"dtos/configurations/{s}.py"],
            "requirements": _REQ.get(s, []),
        }
        for s in (
            "mongo", "cassandra", "scylla", "dynamo", "cosmos", "elasticsearch",
            "graph", "slack", "datadog", "telemetry",
        )
    },
    "payments": {
        "dirs": ["config/payments", "dtos/configurations/payments"],
        "files": ["configurations/payments.py"],
        "requirements": ["fastmvc_payments>=0.1.0", "boto3>=1.28.0,<2.0.0"],
    },
    "identity": {
        "dirs": ["config/identity", "dtos/configurations/identity", "services/auth"],
        "files": [],
        "remove_files": ["configurations/identity.py"],
        "requirements": ["fastmvc_identity>=0.1.0", "python-jose[cryptography]>=3.3.0,<4.0.0"],
    },
    "queues": {
        "dirs": ["config/queues", "services/queues"],
        "files": ["configurations/queues.py", "dtos/configurations/queues.py"],
        "requirements": ["fastmvc_queues>=0.1.0", "pika>=1.3.0,<2.0.0", "nats-py>=2.0.0,<3.0.0", "boto3>=1.28.0,<2.0.0"],
    },
    "jobs": {
        "dirs": ["config/jobs", "services/jobs"],
        "files": ["configurations/jobs.py", "dtos/configurations/jobs.py"],
        "requirements": ["fastmvc_jobs>=0.1.0", "celery>=5.3.0,<6.0.0"],
    },
    "storage": {
        "dirs": ["config/storage", "services/storage"],
        "files": ["configurations/storage.py", "dtos/configurations/storage.py"],
        "requirements": ["fastmvc_storage>=0.1.0", "boto3>=1.28.0,<2.0.0", "google-cloud-storage>=2.10.0,<3.0.0", "azure-storage-blob>=12.17.0,<13.0.0"],
    },
    "streams": {
        "dirs": ["config/streams", "services/streams"],
        "files": ["configurations/streams.py", "dtos/configurations/streams.py"],
        "requirements": ["aiokafka>=0.8.0,<1.0.0"],
    },
    "email": {
        "dirs": ["config/email", "services/communications"],
        "files": ["configurations/email.py", "dtos/configurations/email.py"],
        "remove_dirs": ["config/email"],
        "remove_files": ["configurations/email.py", "dtos/configurations/email.py"],
        "requirements": ["sendgrid>=6.11.0,<7.0.0"],
    },
}


@add.command("service")
@click.argument(
    "service_name",
    type=click.Choice(list(SERVICE_SPECS.keys()), case_sensitive=False),
)
def add_service(service_name: str):
    """
    Add an infrastructure service integration to an existing FastMVC project.

    This command copies the relevant config/ and DTO/configuration modules
    from the FastMVC template into the current project without overwriting
    existing files, so the server keeps working after the addition.

    Datastores (mongo, cassandra, scylla, cosmos, elasticsearch, etc.) and
    identity/payments use fastmvc_core and optional packages (fastmvc_identity,
    fastmvc_payments). For multi-package setups, run install_packages.sh in
    the documented order (core → fastmvc_db → … → main).

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
    spec = SERVICE_SPECS.get(service_name)
    if not spec:
        click.secho(f"✗ Unsupported service: {service_name}", fg="red")
        sys.exit(1)

    for d in spec.get("dirs", []):
        _copy_dir(d)
    for f in spec.get("files", []):
        _copy_file(f)

    requirements_path = project_path / "requirements.txt"
    if requirements_path.exists() and spec.get("requirements"):
        existing = requirements_path.read_text().splitlines()
        existing_lower = {line.strip().split("==")[0].split(">=")[0].lower() for line in existing if line and not line.lstrip().startswith("#")}

        def _ensure(lines: list[str], package: str) -> None:
            name = package.split("==")[0].split(">=")[0].lower()
            if name not in existing_lower:
                lines.append(package)
                existing_lower.add(name)

        updated = existing[:]
        for pkg in spec["requirements"]:
            _ensure(updated, pkg)
        if updated != existing:
            requirements_path.write_text("\n".join(updated) + "\n")

    click.echo()
    click.secho("✓ Service integration files added.", fg="green", bold=True)
    click.echo("  → Update the corresponding config/*/config.json to enable the service.")
    if service_name in {"mongo", "cassandra", "scylla", "dynamo", "cosmos", "elasticsearch", "graph", "slack", "datadog", "telemetry"}:
        click.echo("  → Config is provided by fastmvc_core; set FASTMVC_CONFIG_BASE to your config/ if needed.")
    for pkg_hint in ("fastmvc_payments", "fastmvc_identity"):
        if any(pkg_hint in r for r in spec.get("requirements", [])):
            click.echo(f"  → Requires {pkg_hint}; config from config/{service_name}/config.json.")
            break
    click.echo("  → No changes were made to app startup, so the server will continue to run.")
    click.echo()


@cli.group()
def remove():
    """
    Remove integrations and scaffolding from an existing FastMVC project.

    This does the inverse of some ``fastmvc add`` operations by deleting
    config/ and DTO/configuration modules for a given service. It is
    conservative and will not touch application code outside those assets.
    """
    pass


@remove.command("service")
@click.argument(
    "service_name",
    type=click.Choice(list(SERVICE_SPECS.keys()), case_sensitive=False),
)
def remove_service(service_name: str):
    """
    Remove an infrastructure service integration from the current project.

    This command deletes config/, configuration, and DTO modules for the
    specified service, and for some services their dedicated service
    directories as well. It will not modify app.py startup wiring.
    """

    click.echo()
    click.secho(f"→ Removing service integration: {service_name}", fg="blue", bold=True)
    click.echo()

    project_path = Path.cwd()
    if not (project_path / "app.py").exists():
        click.secho(
            "✗ Not in a FastMVC project directory. "
            "Run this command from your project root.",
            fg="red",
        )
        sys.exit(1)

    def _rm_dir(rel: str) -> None:
        dst = project_path / rel
        if not dst.exists():
            return
        shutil.rmtree(dst, ignore_errors=True)
        click.secho(f"  ✓ Removed directory: {rel}", fg="green")

    def _rm_file(rel: str) -> None:
        dst = project_path / rel
        if not dst.exists():
            return
        try:
            dst.unlink()
            click.secho(f"  ✓ Removed file: {rel}", fg="green")
        except OSError:
            click.secho(f"  • Could not remove file (skipped): {rel}", fg="yellow")

    service_name = service_name.lower()
    spec = SERVICE_SPECS.get(service_name)
    if not spec:
        click.secho(f"✗ Unsupported service: {service_name}", fg="red")
        sys.exit(1)

    remove_dirs = spec.get("remove_dirs", spec.get("dirs", []))
    remove_files = spec.get("remove_files", spec.get("files", []))
    for d in remove_dirs:
        _rm_dir(d)
    for f in remove_files:
        _rm_file(f)

    # We intentionally do NOT try to remove dependencies from requirements.txt
    # because other parts of the application may still rely on them.

    click.echo()
    click.secho("✓ Service integration assets removed.", fg="green", bold=True)
    click.echo("  → Review imports and usage in your code to remove any dead references.")
    click.echo()


# ============================================================================
# MIGRATE COMMAND GROUP
# ============================================================================


def _alembic_run(argv: list[str]) -> subprocess.CompletedProcess:
    """Run Alembic with resolved ``alembic.ini`` (walks up from cwd)."""
    ini = find_alembic_ini()
    cwd = alembic_cwd(ini)
    cmd = alembic_base_args(ini) + argv
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def _require_alembic_ini() -> None:
    if find_alembic_ini() is None:
        click.secho("✗ alembic.ini not found. Are you in a FastMVC project?", fg="red")
        sys.exit(1)


def _find_project_root() -> Path:
    """Directory containing ``fastmvc.toml`` or ``pyproject.toml``, else cwd."""
    cur = Path.cwd().resolve()
    for directory in [cur, *cur.parents]:
        if (directory / "fastmvc.toml").is_file():
            return directory
        if (directory / "pyproject.toml").is_file():
            return directory
    return cur


def _pyproject_has_mypy_section(pyproject: Path) -> bool:
    try:
        raw = pyproject.read_bytes()
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib  # type: ignore[import-not-found]

        data = tomllib.loads(raw.decode("utf-8"))
    except Exception:
        return False
    return "mypy" in (data.get("tool") or {})


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

    if find_alembic_ini() is None:
        click.secho("✗ alembic.ini not found. Are you in a FastMVC project?", fg="red")
        sys.exit(1)

    try:
        cmd = ["revision"]
        if autogenerate:
            cmd.append("--autogenerate")
        cmd.extend(["-m", message])

        result = _alembic_run(cmd)

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

    _require_alembic_ini()
    try:
        result = _alembic_run(["upgrade", revision])

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

    _require_alembic_ini()
    try:
        result = _alembic_run(["downgrade", revision])

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

    _require_alembic_ini()
    try:
        result = _alembic_run(["current"])

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

    _require_alembic_ini()
    try:
        cmd = ["history"]
        if verbose:
            cmd.append("--verbose")

        result = _alembic_run(cmd)

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
    click.echo("  fastmvc doctor [--check-db]      → Env / deps / optional DB check")
    click.echo("  fastmvc add entity <name>        → Add CRUD entity")
    click.echo("  fastmvc migrate generate <msg>   → Create migration")
    click.echo("  fastmvc migrate upgrade          → Apply migrations")
    click.echo("  fastmvc migrate downgrade        → Rollback migrations")
    click.echo("  fastmvc migrate status           → Show current status")
    click.echo("  fastmvc version [--check-pypi]   → Show version / PyPI latest")
    click.echo("  fastmvc lint                     → Ruff (+ mypy if configured)")
    click.echo("  fastmvc run                      → pre_run hooks + uvicorn")
    click.echo()


@cli.command()
@click.option(
    "--check-pypi",
    is_flag=True,
    help="Show latest pyfastmvc version on PyPI (also if FASTMVC_CHECK_PYPI=1).",
)
def version(check_pypi: bool):
    """Display the FastMVC version; optional PyPI latest for update hints."""
    click.echo(f"FastMVC v{__version__}")
    if check_pypi or os.environ.get("FASTMVC_CHECK_PYPI") == "1":
        from fastmvc_cli.pypi_version import fetch_pypi_latest_version

        latest = fetch_pypi_latest_version()
        if latest:
            click.echo(f"PyPI latest: {latest}")
            if latest != __version__:
                click.secho("Update: pip install -U pyfastmvc", fg="yellow")
        else:
            click.secho("(Could not reach PyPI for version check.)", dim=True)


@cli.command()
@click.option(
    "--no-mypy",
    is_flag=True,
    help="Skip mypy even when [tool.mypy] is present in pyproject.toml.",
)
def lint(no_mypy: bool):
    """
    Run Ruff on the project tree; run mypy when ``[tool.mypy]`` exists in pyproject.toml.

    Uses the nearest project root (directory with fastmvc.toml or pyproject.toml).
    """
    root = _find_project_root()
    try:
        ruff = subprocess.run(["ruff", "check", "."], cwd=root)
    except FileNotFoundError:
        click.secho("✗ ruff not found. Install with: pip install ruff", fg="red")
        sys.exit(1)
    if ruff.returncode != 0:
        sys.exit(ruff.returncode)

    pp = root / "pyproject.toml"
    if no_mypy or not pp.is_file() or not _pyproject_has_mypy_section(pp):
        return
    try:
        mypy = subprocess.run([sys.executable, "-m", "mypy", "."], cwd=root)
    except FileNotFoundError:
        click.secho("✗ mypy not found. Install with: pip install mypy", fg="red")
        sys.exit(1)
    sys.exit(mypy.returncode)


@cli.command()
@click.option("--app", default="app:app", show_default=True, help="ASGI app import string.")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, type=int, show_default=True)
@click.option("--reload/--no-reload", default=True, help="Dev auto-reload (default: on).")
def run(app: str, host: str, port: int, reload: bool):
    """
    Run ``pre_run`` hooks from fastmvc.toml / pyproject, then start uvicorn.

    Example: ``fastmvc run`` (same as ``python -m uvicorn app:app --reload``).
    """
    project_root = _find_project_root()
    try:
        run_pre_run(project_root)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    cmd = [sys.executable, "-m", "uvicorn", app, "--host", host, "--port", str(port)]
    if reload:
        cmd.append("--reload")
    sys.exit(subprocess.run(cmd).returncode)


@cli.command("doctor")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Project root (default: current directory).",
)
@click.option(
    "--check-db/--no-check-db",
    default=False,
    help="Run SELECT 1 using DATABASE_URL or DATABASE_* (loads .env when present).",
)
@click.option(
    "--no-dotenv",
    is_flag=True,
    default=False,
    help="Do not load .env from the project directory.",
)
def doctor_cli(project_dir: Path | None, check_db: bool, no_dotenv: bool):
    """
    Check Python version, core imports, project files, and optionally database connectivity.

    Run from a generated project root to validate .env and DATABASE_* settings.
    """
    sys.exit(
        run_doctor(
            project_dir=project_dir,
            check_db=check_db,
            load_dotenv_file=not no_dotenv,
        )
    )


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
