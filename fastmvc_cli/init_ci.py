"""
Non-interactive ``fastmvc init --ci`` implementation.
"""

from __future__ import annotations

import base64
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

import click

from fastmvc_cli.generator import ProjectGenerator
from fastmvc_cli.hooks import run_post_generate
from fastmvc_cli.presets import apply_template_pack
from fastmvc_cli.scaffold_helpers import (
    write_ci_workflow,
    write_contributing,
    write_license,
    write_precommit,
    write_pyproject,
)


def run_init_ci(project_name: str, output_dir: str, *, force: bool) -> None:
    """Create a project with CI-friendly defaults (no prompts)."""
    click.echo()
    click.secho(f"→ CI init: {project_name}", fg="cyan", bold=True)

    jwt_secret = secrets.token_urlsafe(32)
    try:
        import bcrypt  # type: ignore[import-untyped]

        bcrypt_salt = bcrypt.gensalt().decode("utf-8")
    except Exception:
        raw = base64.b64encode(os.urandom(16)).decode("utf-8")
        bcrypt_salt = f"$2b$12${raw[:22]}"

    generator = ProjectGenerator(
        project_name=project_name,
        output_dir=output_dir,
        init_git=True,
        create_venv=False,
        install_deps=False,
    )
    generator.api_preset = "crud"
    generator.db_backend = "postgres"
    generator.use_redis = True
    generator.use_mongo = False
    generator.use_cassandra = False
    generator.use_dynamo = False
    generator.use_cosmos = False
    generator.use_scylla = False
    generator.use_elasticsearch = False
    generator.use_neo4j = False
    generator.use_email = False
    generator.use_slack = False
    generator.use_datadog = False
    generator.use_telemetry = False
    generator.use_payments = False
    generator.use_rabbitmq = False
    generator.use_sqs = False
    generator.use_service_bus = False
    generator.use_celery = False
    generator.use_s3 = False
    generator.use_gcs = False
    generator.use_azure_blob = False
    generator.use_meilisearch = False
    generator.use_typesense = False
    generator.use_analytics = False
    generator.use_events = False
    generator.use_vault = False
    generator.use_aws_secrets = False
    generator.use_feature_flags = False
    generator.use_identity = False
    generator.use_streams = False
    generator.app_port = 8000
    generator.db_name = project_name
    generator.db_host = "localhost"
    generator.db_port = "5432"
    generator.jwt_secret = jwt_secret
    generator.bcrypt_salt = bcrypt_salt
    generator.cors_origins = "http://localhost:3000,http://localhost:8000"
    generator.enable_auth = True
    generator.enable_user_mgmt = True
    generator.enable_product_crud = True
    generator.layout = "monolith"
    generator.enable_alembic = True
    generator.enable_ruff = True
    generator.enable_black = True
    generator.enable_isort = True
    generator.enable_mypy = False
    generator.enable_precommit = True
    generator.enable_ci = True
    generator.enable_runtime_helpers = True
    generator.include_docker_compose = True

    try:
        apply_template_pack(generator, "standard")
    except ValueError as e:
        click.secho(str(e), fg="red")
        sys.exit(1)

    if generator.project_path.exists():
        if not force:
            click.secho(
                "Directory exists. Re-run with --force to overwrite.",
                fg="red",
            )
            sys.exit(1)
        shutil.rmtree(generator.project_path)

    generator.generate()

    env_example = generator.project_path / ".env.example"
    env_file = generator.project_path / ".env"
    if env_example.exists():
        shutil.copy2(env_example, env_file)

    license_key = "mit"
    write_license(generator.project_path / "LICENSE", license_key, project_name)
    write_contributing(generator.project_path / "CONTRIBUTING.md")
    write_pyproject(
        generator.project_path / "pyproject.toml",
        generator.enable_ruff,
        generator.enable_black,
        generator.enable_isort,
        generator.enable_mypy,
    )
    write_precommit(
        generator.project_path / ".pre-commit-config.yaml",
        generator.enable_ruff,
        generator.enable_black,
        generator.enable_isort,
        generator.enable_mypy,
    )
    ci_dir = generator.project_path / ".github" / "workflows"
    ci_dir.mkdir(parents=True, exist_ok=True)
    write_ci_workflow(
        ci_dir / "ci.yml",
        generator.enable_ruff,
        generator.enable_black,
        generator.enable_isort,
        generator.enable_mypy,
    )

    try:
        run_post_generate(generator.project_path)
    except subprocess.CalledProcessError as e:
        click.secho(f"✗ post_generate hook failed (exit {e.returncode})", fg="red")
        sys.exit(1)

    click.echo()
    click.secho("✓ CI project generated successfully!", fg="green", bold=True)
    click.echo(f"  Location: {generator.project_path}")
