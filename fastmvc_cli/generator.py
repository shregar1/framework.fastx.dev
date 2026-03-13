"""
FastMVC Project Generator.

This module handles the generation of new FastMVC projects from
the template. It copies all necessary files, customizes them with
the project name, and optionally initializes git and virtual environment.

Classes:
    ProjectGenerator: Main class for generating new projects.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import click


class ProjectGenerator:
    """
    Generator for new FastMVC projects.

    This class handles copying template files, customizing project names,
    and setting up the development environment for a new FastMVC project.

    Attributes:
        project_name (str): Name of the new project.
        output_dir (Path): Directory where project will be created.
        project_path (Path): Full path to the new project.
        init_git (bool): Whether to initialize git repository.
        create_venv (bool): Whether to create virtual environment.
        install_deps (bool): Whether to install dependencies.

    Example:
        >>> generator = ProjectGenerator("my_api", "~/projects")
        >>> generator.generate()
    """

    # Directories to copy from template
    TEMPLATE_DIRS = [
        "abstractions",
        "config",
        "configurations",
        "constants",
        "controllers",
        "dependencies",
        "dtos",
        "errors",
        "middlewares",
        "migrations",
        "models",
        "repositories",
        "services",
        "tests",
        "utilities",
    ]

    # Files to copy from template
    TEMPLATE_FILES = [
        "app.py",
        "start_utils.py",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile",
        "pytest.ini",
        ".coveragerc",
        "LICENSE",
        "alembic.ini",
    ]

    # Directories/files to exclude when copying
    EXCLUDE_PATTERNS = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".env",
        "htmlcov",
        ".coverage",
        "*.egg-info",
        "dist",
        "build",
        ".pytest_cache",
        "fastmvc_cli",  # Don't copy CLI into generated projects
    ]

    def __init__(
        self,
        project_name: str,
        output_dir: str = ".",
        init_git: bool = True,
        create_venv: bool = False,
        install_deps: bool = False,
    ):
        """
        Initialize the project generator.

        Args:
            project_name: Name of the new project.
            output_dir: Directory where project will be created.
            init_git: Whether to initialize git repository.
            create_venv: Whether to create virtual environment.
            install_deps: Whether to install dependencies.
        """
        self.project_name = self._sanitize_name(project_name)
        self.output_dir = Path(output_dir).resolve()
        self.project_path = self.output_dir / self.project_name
        self.init_git = init_git
        self.create_venv = create_venv
        self.install_deps = install_deps

        # Get the template path (FastMVC package location)
        self.template_path = self._get_template_path()

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize the project name for use as directory and package name.

        Args:
            name: Raw project name.

        Returns:
            Sanitized project name.
        """
        # Replace hyphens with underscores for Python compatibility
        sanitized = name.replace("-", "_")
        # Remove any characters that aren't alphanumeric or underscore
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "", sanitized)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = "_" + sanitized
        # Use a neutral default if nothing valid remains
        return sanitized or "my_project"

    def _get_template_path(self) -> Path:
        """
        Get the path to the FastMVC template files.

        Returns:
            Path to the template directory.
        """
        # The template is the FastMVC package itself
        # When installed via pip, the package is in site-packages
        # We need to find it relative to this module

        # First, try to find it relative to this file (for development)
        cli_path = Path(__file__).parent
        template_path = cli_path.parent

        if (template_path / "app.py").exists():
            return template_path

        # If not found, try the installed package location
        try:
            import fastmvc_cli
            package_path = Path(fastmvc_cli.__file__).parent.parent
            if (package_path / "app.py").exists():
                return package_path
        except ImportError:
            pass

        # Fallback: use current working directory
        cwd = Path.cwd()
        if (cwd / "app.py").exists():
            return cwd

        raise FileNotFoundError(
            "Could not find FastMVC template files. "
            "Make sure FastMVC is installed correctly."
        )

    def _should_exclude(self, path: Path) -> bool:
        """
        Check if a path should be excluded from copying.

        Args:
            path: Path to check.

        Returns:
            True if path should be excluded.
        """
        name = path.name

        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.startswith("*"):
                # Wildcard pattern
                if name.endswith(pattern[1:]):
                    return True
            else:
                # Exact match
                if name == pattern:
                    return True

        return False

    def generate(self):
        """
        Generate the new FastMVC project.

        This is the main method that orchestrates the entire generation process.
        It creates the project directory, copies template files, customizes
        configurations, and optionally sets up git and virtual environment.

        Raises:
            FileExistsError: If project directory already exists.
            Exception: If any step of generation fails.
        """
        click.secho(f"→ Creating project: {self.project_name}", fg="blue")
        click.secho(f"  Location: {self.project_path}", fg="white", dim=True)
        click.echo()

        # Check if project directory already exists
        if self.project_path.exists():
            raise FileExistsError(
                f"Directory '{self.project_path}' already exists. "
                "Choose a different name or delete the existing directory."
            )

        # Create project directory
        self._step("Creating project directory")
        self.project_path.mkdir(parents=True)

        # Copy template directories
        self._step("Copying template files")
        self._copy_template()

        # Create .env.example
        self._step("Creating environment configuration")
        self._create_env_example()

        # Remove optional service configs that are not enabled for this project
        self._step("Pruning unused service configurations")
        self._prune_optional_configs()

        # Create .gitignore
        self._step("Creating .gitignore")
        self._create_gitignore()

        # Create project README
        self._step("Creating README.md")
        self._create_readme()

        # Create runtime helper scripts (Makefile, scripts)
        self._step("Creating runtime helpers")
        self._create_runtime_helpers()

        # Update configurations with project name
        self._step("Customizing configurations")
        self._customize_configs()

        # Initialize git repository
        if self.init_git:
            self._step("Initializing git repository")
            self._init_git()

        # Create virtual environment
        if self.create_venv:
            self._step("Creating virtual environment")
            self._create_venv()

        # Install dependencies
        if self.install_deps:
            self._step("Installing dependencies")
            self._install_deps()

    def _step(self, message: str):
        """Display a step message."""
        click.secho(f"  ● {message}...", fg="white")

    def _copy_template(self):
        """Copy all template directories and files to the new project."""
        # Copy directories
        for dir_name in self.TEMPLATE_DIRS:
            src = self.template_path / dir_name
            dst = self.project_path / dir_name

            if src.exists() and src.is_dir():
                self._copy_directory(src, dst)

        # Copy individual files
        for file_name in self.TEMPLATE_FILES:
            src = self.template_path / file_name
            dst = self.project_path / file_name

            if src.exists() and src.is_file():
                shutil.copy2(src, dst)

    def _copy_directory(self, src: Path, dst: Path):
        """
        Recursively copy a directory, excluding unwanted files.

        Args:
            src: Source directory path.
            dst: Destination directory path.
        """
        if self._should_exclude(src):
            return

        dst.mkdir(parents=True, exist_ok=True)

        for item in src.iterdir():
            if self._should_exclude(item):
                continue

            dst_item = dst / item.name

            if item.is_dir():
                self._copy_directory(item, dst_item)
            else:
                shutil.copy2(item, dst_item)

    def _prune_optional_configs(self) -> None:
        """
        Remove configuration files/directories for services that are not enabled.

        This keeps generated projects lean by only including configs for the
        services explicitly selected in the project wizard (or defaults).
        """
        # Flags are optionally set by the CLI wizard; fall back to False.
        optional_services: dict[str, bool] = {
            "mongo": getattr(self, "use_mongo", False),
            "cassandra": getattr(self, "use_cassandra", False),
            "scylla": getattr(self, "use_scylla", False),
            "dynamo": getattr(self, "use_dynamo", False),
            "cosmos": getattr(self, "use_cosmos", False),
            "elasticsearch": getattr(self, "use_elasticsearch", False),
            "graph": getattr(self, "use_neo4j", False),
            "search": bool(
                getattr(self, "use_meilisearch", False)
                or getattr(self, "use_typesense", False)
            ),
            "email": getattr(self, "use_email", False),
            "slack": getattr(self, "use_slack", False),
            "datadog": getattr(self, "use_datadog", False),
            "telemetry": getattr(self, "use_telemetry", False),
            "payments": getattr(self, "use_payments", False),
            "identity": getattr(self, "use_identity", False),
            # Grouped configs: queues and jobs
            "queues": bool(
                getattr(self, "use_rabbitmq", False)
                or getattr(self, "use_sqs", False)
                or getattr(self, "use_service_bus", False)
            ),
            "jobs": bool(
                getattr(self, "use_celery", False)
            ),
            # Grouped config: storage
            "storage": bool(
                getattr(self, "use_s3", False)
                or getattr(self, "use_gcs", False)
                or getattr(self, "use_azure_blob", False)
            ),
            # Analytics/event tracking
            "analytics": getattr(self, "use_analytics", False),
            "events": getattr(self, "use_events", False),
            # Secrets and feature flags
            "secrets": bool(
                getattr(self, "use_vault", False)
                or getattr(self, "use_aws_secrets", False)
            ),
            "feature_flags": getattr(self, "use_feature_flags", False),
            # Realtime / collaboration settings
            "realtime": getattr(self, "use_realtime", False),
            # Streams / HFT hub
            "streams": getattr(self, "use_streams", False),
        }

        for service_name, enabled in optional_services.items():
            if enabled:
                continue

            # Remove config/<service>/ directory
            cfg_dir = self.project_path / "config" / service_name
            if cfg_dir.exists():
                shutil.rmtree(cfg_dir, ignore_errors=True)

            # Remove configurations/<service>.py module
            cfg_module = self.project_path / "configurations" / f"{service_name}.py"
            if cfg_module.exists():
                try:
                    cfg_module.unlink()
                except OSError:
                    pass

            # Remove dtos/configurations/<service>.py DTO module
            dto_module = (
                self.project_path / "dtos" / "configurations" / f"{service_name}.py"
            )
            if dto_module.exists():
                try:
                    dto_module.unlink()
                except OSError:
                    pass

    def _create_env_example(self):
        """Create the .env.example file with default configuration."""
        # Read preset options if they exist (set by the CLI wizard)
        db_backend = getattr(self, "db_backend", "postgres")
        use_redis = getattr(self, "use_redis", True)
        use_mongo = getattr(self, "use_mongo", False)
        use_cassandra = getattr(self, "use_cassandra", False)
        use_dynamo = getattr(self, "use_dynamo", False)
        use_cosmos = getattr(self, "use_cosmos", False)
        use_scylla = getattr(self, "use_scylla", False)
        use_elasticsearch = getattr(self, "use_elasticsearch", False)
        use_meilisearch = getattr(self, "use_meilisearch", False)
        use_typesense = getattr(self, "use_typesense", False)
        use_email = getattr(self, "use_email", False)
        use_slack = getattr(self, "use_slack", False)
        use_datadog = getattr(self, "use_datadog", False)
        use_telemetry = getattr(self, "use_telemetry", False)
        use_payments = getattr(self, "use_payments", False)
        use_rabbitmq = getattr(self, "use_rabbitmq", False)
        use_sqs = getattr(self, "use_sqs", False)
        use_celery = getattr(self, "use_celery", False)
        use_s3 = getattr(self, "use_s3", False)
        use_gcs = getattr(self, "use_gcs", False)
        use_azure_blob = getattr(self, "use_azure_blob", False)
        use_analytics = getattr(self, "use_analytics", False)
        use_vault = getattr(self, "use_vault", False)
        use_aws_secrets = getattr(self, "use_aws_secrets", False)
        use_feature_flags = getattr(self, "use_feature_flags", False)
        use_identity = getattr(self, "use_identity", False)
        api_preset = getattr(self, "api_preset", "crud")
        profile = getattr(self, "profile", "standard")
        sqlalchemy_mode = getattr(self, "sqlalchemy_mode", "sync")
        app_port = getattr(self, "app_port", 8000)
        db_name = getattr(self, "db_name", self.project_name)
        db_host = getattr(self, "db_host", "localhost")
        db_port = getattr(self, "db_port", "5432" if db_backend == "postgres" else "3306")
        jwt_secret = getattr(
            self,
            "jwt_secret",
            "your-super-secret-jwt-key-change-this-in-production",
        )
        bcrypt_salt = getattr(
            self,
            "bcrypt_salt",
            "$2b$12$LQv3c1yqBWVHxkd0LHAkCO",
        )
        cors_origins = getattr(
            self,
            "cors_origins",
            "http://localhost:3000,http://localhost:8000",
        )

        lines = [
            f"# {self.project_name.upper()} Environment Configuration",
            "# Copy this file to .env and update with your values",
            "",
            "# Preset information",
            f"# API_PRESET={api_preset}",
            f"# PROFILE={profile}",
            f"# DB_BACKEND={db_backend}",
            f"# SQLALCHEMY_MODE={sqlalchemy_mode}",
            "",
            "# Application Settings",
            f'APP_NAME="{self.project_name}"',
            'APP_ENV="development"',
            'APP_DEBUG="true"',
            'APP_HOST="0.0.0.0"',
            f'APP_PORT="{app_port}"',
            "",
            "# Database Configuration",
        ]

        if db_backend == "sqlite":
            lines.extend(
                [
                    f'DATABASE_URL="sqlite:///./{db_name}.db"',
                    '# NOTE: SQLite is file-based; host/port/user/password are not used.',
                ]
            )
        else:
            # mysql or postgres-style separate settings
            db_user = getattr(self, "db_user", "postgres" if db_backend == "postgres" else "root")
            db_password = getattr(
                self,
                "db_password",
                "postgres123" if db_backend == "postgres" else "mysql123",
            )
            lines.extend(
                [
                    f'DATABASE_HOST="{db_host}"',
                    f'DATABASE_PORT="{db_port}"',
                    f'DATABASE_NAME="{db_name}"',
                    f'DATABASE_USER="{db_user}"',
                    f'DATABASE_PASSWORD="{db_password}"',
                    'DATABASE_POOL_SIZE="5"',
                    'DATABASE_MAX_OVERFLOW="10"',
                ]
            )

        lines.append("")

        if use_redis:
            lines.extend(
                [
                    "# Redis Configuration",
                    'REDIS_HOST="localhost"',
                    'REDIS_PORT="6379"',
                    'REDIS_PASSWORD="test123"',
                    'REDIS_DB="0"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Redis Configuration (disabled in this preset)",
                    '# REDIS_HOST="localhost"',
                    '# REDIS_PORT="6379"',
                    '# REDIS_PASSWORD="test123"',
                    '# REDIS_DB="0"',
                    "",
                ]
            )

        # Optional document / NoSQL / cloud data stores
        if use_mongo:
            lines.extend(
                [
                    "# MongoDB Configuration",
                    'MONGO_ENABLED="true"',
                    'MONGO_URI="mongodb://localhost:27017"',
                    f'MONGO_DATABASE="{db_name}"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# MongoDB Configuration (disabled in this preset)",
                    '# MONGO_ENABLED="false"',
                    '# MONGO_URI="mongodb://localhost:27017"',
                    f'# MONGO_DATABASE="{db_name}"',
                    "",
                ]
            )

        if use_cassandra:
            lines.extend(
                [
                    "# Cassandra Configuration",
                    'CASSANDRA_ENABLED="true"',
                    'CASSANDRA_CONTACT_POINTS="127.0.0.1"',
                    'CASSANDRA_PORT="9042"',
                    f'CASSANDRA_KEYSPACE="{db_name}_ks"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Cassandra Configuration (disabled in this preset)",
                    '# CASSANDRA_ENABLED="false"',
                    '# CASSANDRA_CONTACT_POINTS="127.0.0.1"',
                    '# CASSANDRA_PORT="9042"',
                    f'# CASSANDRA_KEYSPACE="{db_name}_ks"',
                    "",
                ]
            )

        if use_scylla:
            lines.extend(
                [
                    "# ScyllaDB Configuration",
                    'SCYLLA_ENABLED="true"',
                    'SCYLLA_CONTACT_POINTS="127.0.0.1"',
                    'SCYLLA_PORT="9042"',
                    f'SCYLLA_KEYSPACE="{db_name}_ks"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# ScyllaDB Configuration (disabled in this preset)",
                    '# SCYLLA_ENABLED="false"',
                    '# SCYLLA_CONTACT_POINTS="127.0.0.1"',
                    '# SCYLLA_PORT="9042"',
                    f'# SCYLLA_KEYSPACE="{db_name}_ks"',
                    "",
                ]
            )

        if use_dynamo:
            lines.extend(
                [
                    "# AWS DynamoDB Configuration",
                    'DYNAMO_ENABLED="true"',
                    'DYNAMO_REGION="us-east-1"',
                    f'DYNAMO_TABLE_PREFIX="{self.project_name}_"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# AWS DynamoDB Configuration (disabled in this preset)",
                    '# DYNAMO_ENABLED="false"',
                    '# DYNAMO_REGION="us-east-1"',
                    f'# DYNAMO_TABLE_PREFIX="{self.project_name}_"',
                    "",
                ]
            )

        if use_cosmos:
            lines.extend(
                [
                    "# Azure Cosmos DB Configuration",
                    'COSMOS_ENABLED="true"',
                    'COSMOS_ACCOUNT_URI="https://your-account.documents.azure.com:443/"',
                    'COSMOS_ACCOUNT_KEY="your-key-here"',
                    f'COSMOS_DATABASE="{db_name}"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Azure Cosmos DB Configuration (disabled in this preset)",
                    '# COSMOS_ENABLED="false"',
                    '# COSMOS_ACCOUNT_URI="https://your-account.documents.azure.com:443/"',
                    '# COSMOS_ACCOUNT_KEY="your-key-here"',
                    f'# COSMOS_DATABASE="{db_name}"',
                    "",
                ]
            )

        if use_elasticsearch:
            lines.extend(
                [
                    "# Elasticsearch Configuration",
                    'ELASTICSEARCH_ENABLED="true"',
                    'ELASTICSEARCH_HOSTS="http://localhost:9200"',
                    'ELASTICSEARCH_USERNAME=""',
                    'ELASTICSEARCH_PASSWORD=""',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Elasticsearch Configuration (disabled in this preset)",
                    '# ELASTICSEARCH_ENABLED="false"',
                    '# ELASTICSEARCH_HOSTS="http://localhost:9200"',
                    '# ELASTICSEARCH_USERNAME=""',
                    '# ELASTICSEARCH_PASSWORD=""',
                    "",
                ]
            )

        if use_email:
            lines.extend(
                [
                    "# Email Configuration (SMTP / SendGrid)",
                    'EMAIL_SMTP_ENABLED="true"',
                    'EMAIL_SMTP_HOST="localhost"',
                    'EMAIL_SMTP_PORT="587"',
                    'EMAIL_SMTP_USERNAME=""',
                    'EMAIL_SMTP_PASSWORD=""',
                    'EMAIL_SMTP_USE_TLS="true"',
                    'EMAIL_SMTP_USE_SSL="false"',
                    'EMAIL_SMTP_DEFAULT_FROM="no-reply@example.com"',
                    'EMAIL_SENDGRID_ENABLED="false"',
                    'EMAIL_SENDGRID_API_KEY=""',
                    'EMAIL_SENDGRID_DEFAULT_FROM="no-reply@example.com"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Email Configuration (disabled in this preset)",
                    '# EMAIL_SMTP_ENABLED="false"',
                    '# EMAIL_SMTP_HOST="localhost"',
                    '# EMAIL_SMTP_PORT="587"',
                    '# EMAIL_SMTP_USERNAME=""',
                    '# EMAIL_SMTP_PASSWORD=""',
                    '# EMAIL_SMTP_USE_TLS="true"',
                    '# EMAIL_SMTP_USE_SSL="false"',
                    '# EMAIL_SMTP_DEFAULT_FROM="no-reply@example.com"',
                    '# EMAIL_SENDGRID_ENABLED="false"',
                    '# EMAIL_SENDGRID_API_KEY=""',
                    '# EMAIL_SENDGRID_DEFAULT_FROM="no-reply@example.com"',
                    "",
                ]
            )

        if use_slack:
            lines.extend(
                [
                    "# Slack Configuration",
                    'SLACK_ENABLED="true"',
                    'SLACK_WEBHOOK_URL=""',
                    'SLACK_BOT_TOKEN=""',
                    'SLACK_DEFAULT_CHANNEL="#alerts"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Slack Configuration (disabled in this preset)",
                    '# SLACK_ENABLED="false"',
                    '# SLACK_WEBHOOK_URL=""',
                    '# SLACK_BOT_TOKEN=""',
                    '# SLACK_DEFAULT_CHANNEL="#alerts"',
                    "",
                ]
            )

        if use_datadog:
            lines.extend(
                [
                    "# Datadog Configuration",
                    'DATADOG_ENABLED="true"',
                    'DATADOG_ENV="development"',
                    'DATADOG_SERVICE="fastmvc-api"',
                    'DATADOG_VERSION=""',
                    'DATADOG_AGENT_HOST="127.0.0.1"',
                    'DATADOG_AGENT_PORT="8126"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Datadog Configuration (disabled in this preset)",
                    '# DATADOG_ENABLED="false"',
                    '# DATADOG_ENV="development"',
                    '# DATADOG_SERVICE="fastmvc-api"',
                    '# DATADOG_VERSION=""',
                    '# DATADOG_AGENT_HOST="127.0.0.1"',
                    '# DATADOG_AGENT_PORT="8126"',
                    "",
                ]
            )

        if use_telemetry:
            lines.extend(
                [
                    "# OpenTelemetry Configuration",
                    'TELEMETRY_ENABLED="true"',
                    'TELEMETRY_EXPORTER="otlp"',
                    'TELEMETRY_ENDPOINT="http://localhost:4317"',
                    'TELEMETRY_PROTOCOL="grpc"',
                    'TELEMETRY_SERVICE_NAME="fastmvc-api"',
                    'TELEMETRY_ENVIRONMENT="development"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# OpenTelemetry Configuration (disabled in this preset)",
                    '# TELEMETRY_ENABLED="false"',
                    '# TELEMETRY_EXPORTER="otlp"',
                    '# TELEMETRY_ENDPOINT="http://localhost:4317"',
                    '# TELEMETRY_PROTOCOL="grpc"',
                    '# TELEMETRY_SERVICE_NAME="fastmvc-api"',
                    '# TELEMETRY_ENVIRONMENT="development"',
                    "",
                ]
            )

        # Queue / messaging configuration
        if use_rabbitmq or use_sqs:
            lines.extend(
                [
                    "# Queue / Messaging Configuration",
                    'QUEUE_BACKEND="rabbitmq"  # or sqs,nats',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Queue / Messaging Configuration (disabled in this preset)",
                    '# QUEUE_BACKEND="none"',
                    "",
                ]
            )

        # Background jobs / workers
        if use_celery:
            lines.extend(
                [
                    "# Celery Worker Configuration",
                    'CELERY_ENABLED="true"',
                    'CELERY_BROKER_URL="redis://localhost:6379/0"',
                    'CELERY_RESULT_BACKEND="redis://localhost:6379/1"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Celery Worker Configuration (disabled in this preset)",
                    '# CELERY_ENABLED="false"',
                    '# CELERY_BROKER_URL="redis://localhost:6379/0"',
                    '# CELERY_RESULT_BACKEND="redis://localhost:6379/1"',
                    "",
                ]
            )

        # Payments
        if use_payments:
            lines.extend(
                [
                    "# Payments Configuration",
                    'PAYMENTS_ENABLED="true"',
                    'PAYMENT_DEFAULT_PROVIDER="stripe"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "# Payments Configuration (disabled in this preset)",
                    '# PAYMENTS_ENABLED="false"',
                    '# PAYMENT_DEFAULT_PROVIDER="stripe"',
                    "",
                ]
            )

        lines.extend(
            [
                "# Security Settings",
                f'JWT_SECRET_KEY="{jwt_secret}"',
                'JWT_ALGORITHM="HS256"',
                'JWT_EXPIRATION_HOURS="24"',
                f'BCRYPT_SALT="{bcrypt_salt}"',
                "",
                "# CORS Settings",
                f'CORS_ORIGINS="{cors_origins}"',
                'CORS_ALLOW_CREDENTIALS="true"',
                'CORS_ALLOW_METHODS="GET,POST,PUT,DELETE,OPTIONS,PATCH"',
                'CORS_ALLOW_HEADERS="*"',
                "",
                 "# Channels (pub-sub) backend",
                 'CHANNEL_BACKEND="none"',
                 "",
                "# Rate Limiting",
                'RATE_LIMIT_REQUESTS_PER_MINUTE="60"',
                'RATE_LIMIT_REQUESTS_PER_HOUR="1000"',
                'RATE_LIMIT_BURST_LIMIT="10"',
                "",
                "# WebRTC Settings",
                'WEBRTC_ENABLED="false"',
                'WEBRTC_STUN_SERVERS=""',
                'WEBRTC_TURN_SERVERS=""',
                "",
                "# Logging",
                'LOG_LEVEL="DEBUG"',
                'LOG_FORMAT="json"',
                "",
            ]
        )

        env_content = "\n".join(lines)
        env_path = self.project_path / ".env.example"
        env_path.write_text(env_content)

    def _create_gitignore(self):
        """Create a comprehensive .gitignore file."""
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
logs/
"""
        gitignore_path = self.project_path / ".gitignore"
        gitignore_path.write_text(gitignore_content)

    def _create_readme(self):
        """Create the project README.md file."""
        project_title = self.project_name.replace('_', ' ').title()
        # Read optional feature/layout flags set by the CLI wizard
        api_preset = getattr(self, "api_preset", "crud")
        db_backend = getattr(self, "db_backend", "postgres")
        use_redis = getattr(self, "use_redis", True)
        layout = getattr(self, "layout", "monolith")
        enable_auth = getattr(self, "enable_auth", True)
        enable_user_mgmt = getattr(self, "enable_user_mgmt", True)
        enable_product_crud = getattr(self, "enable_product_crud", True)
        enable_alembic = getattr(self, "enable_alembic", True)

        features_line = []
        if enable_auth:
            features_line.append("auth")
        if enable_user_mgmt:
            features_line.append("user-management")
        if enable_product_crud:
            features_line.append("product-crud-example")
        if not features_line:
            features_line.append("core-api")

        features_str = ", ".join(features_line)

        readme_content = f"""# {project_title}

Production-ready FastAPI service generated from a template.

## Project configuration

- API preset: **{api_preset}**
- DB backend: **{db_backend}**
- Redis: **{"enabled" if use_redis else "disabled"}**
- Layout: **{layout}**
- Features: **{features_str}**
- Alembic migrations: **{"enabled" if enable_alembic else "disabled"}**

## Quick Start

### 1. Setup environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

pip install -r requirements.txt
cp .env.example .env
```

### 2. Start infrastructure (optional)

```bash
docker-compose up -d
```

### 3. Run the API

```bash
python -m uvicorn app:app --reload
```

- API:  http://localhost:8000
- Docs: http://localhost:8000/docs

## Project structure

```text
{self.project_name}/
├── app.py              # FastAPI entry point
├── start_utils.py      # Startup configuration
├── abstractions/       # Base interfaces & contracts
├── controllers/        # HTTP route handlers
├── services/           # Business logic
├── repositories/       # Data access layer
├── models/             # SQLAlchemy ORM models
├── dtos/               # Data Transfer Objects
├── middlewares/        # Request processing
├── migrations/         # Alembic migrations
├── tests/              # Test suite
└── docker-compose.yml  # Optional infrastructure
```

## Testing

```bash
pytest
pytest --cov=. --cov-report=html
```

## Database migrations (Alembic)

Alembic support is already wired via the `fastmvc` CLI:

```bash
# Generate a new migration from model changes
fastmvc migrate generate "describe your change"

# Apply all pending migrations
fastmvc migrate upgrade

# Roll back one step
fastmvc migrate downgrade -1

# Show current revision and history
fastmvc migrate status
fastmvc migrate history
```

The Alembic configuration lives in `alembic.ini` and the `migrations/` package.
The `DATABASE_*` values in `.env` control which database the migrations apply to.

If you prefer Make, you can also run:

```bash
make migrate
```

## License

This project is licensed under the MIT License.
"""
        readme_path = self.project_path / "README.md"
        readme_path.write_text(readme_content)

    def _create_runtime_helpers(self):
        """Create Makefile and helper scripts for common tasks."""
        # Respect optional flag from CLI; default to enabled
        enable_helpers = getattr(self, "enable_runtime_helpers", True)
        if not enable_helpers:
            return

        makefile_content = """# Common developer commands

.PHONY: dev test lint fmt migrate db-up db-down health

dev:
\tuvicorn app:app --reload

test:
\tpytest

lint:
\truff . || true

fmt:
\tblack . || true
\tisort . || true

migrate:
\tfastmvc migrate upgrade

db-up:
\tdocker-compose up -d postgres redis

db-down:
\tdocker-compose down

health:
\tpython scripts/health_check.py
"""
        (self.project_path / "Makefile").write_text(makefile_content)

        scripts_dir = self.project_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        bootstrap_sh = """#!/usr/bin/env bash
set -e

echo "Starting local infrastructure (Postgres + Redis) with docker-compose..."
docker-compose up -d postgres redis

echo "Running database migrations..."
fastmvc migrate upgrade || echo "fastmvc migrate upgrade failed or not configured."

echo "Done."
"""
        health_py = """import sys

import httpx


def main() -> int:
    url = "http://localhost:8000/health"
    try:
        resp = httpx.get(url, timeout=5.0)
    except Exception as exc:  # pragma: no cover - network error path
        print(f"Health check failed: {exc}")
        return 1

    if resp.status_code != 200:
        print(f"Health check failed with status {resp.status_code}: {resp.text}")
        return 1

    print("Health check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""
        (scripts_dir / "bootstrap.sh").write_text(bootstrap_sh)
        (scripts_dir / "health_check.py").write_text(health_py)

    def _customize_configs(self):
        """Update configuration files with the project name."""
        # Update docker-compose.yml
        docker_compose_path = self.project_path / "docker-compose.yml"
        if docker_compose_path.exists():
            content = docker_compose_path.read_text()

            # Network and image names
            content = content.replace("fastmvc_net", f"{self.project_name}_net")
            content = content.replace("fastmvc:", f"{self.project_name}:")
            content = content.replace('POSTGRES_DB: fastmvc', f'POSTGRES_DB: {self.project_name}')

            # Align exposed FastAPI port with selected APP_PORT if available
            app_port = getattr(self, "app_port", 8000)
            content = content.replace(
                '      - "8003:8003"',
                f'      - "{app_port}:{app_port}"',
            )

            # Respect selected backing services: Redis and Postgres
            use_redis = getattr(self, "use_redis", True)
            db_backend = getattr(self, "db_backend", "postgres")

            # Helper to remove a whole service block by name (very simple text slicing)
            def _remove_service_block(text: str, service_name: str) -> str:
                marker = f"\n  {service_name}:"
                start = text.find(marker)
                if start == -1:
                    return text
                # Find the next top-level service or end of file
                next_service_idx = text.find("\n  ", start + 1)
                if next_service_idx == -1:
                    return text[:start]
                return text[:start] + text[next_service_idx:]

            # Remove Redis service and dependency if Redis is not used
            if not use_redis:
                content = _remove_service_block(content, "redis")
                content = content.replace("      - redis\n", "")

            # If database backend is not Postgres (e.g. sqlite / mysql), drop Postgres
            if db_backend != "postgres":
                content = _remove_service_block(content, "postgres")
                content = content.replace("      - postgres\n", "")

            docker_compose_path.write_text(content)

        # Update DB config for Alembic / runtime if present
        db_config_path = self.project_path / "config" / "db" / "config.json"
        if db_config_path.exists():
            try:
                import json

                with db_config_path.open() as f:
                    cfg = json.load(f)

                # Basic alignment with wizard choices (host/port/database only;
                # credentials are intentionally left for the user to fill).
                db_backend = getattr(self, "db_backend", "postgres")
                db_name = getattr(self, "db_name", self.project_name)
                db_host = getattr(self, "db_host", "localhost")
                db_port = getattr(
                    self,
                    "db_port",
                    "5432" if db_backend == "postgres" else "3306",
                )

                cfg["host"] = db_host
                cfg["port"] = int(db_port)
                cfg["database"] = db_name

                # Adjust connection_string driver based on backend
                if db_backend == "mysql":
                    cfg["connection_string"] = (
                        "mysql+pymysql://{user_name}:{password}@{host}:{port}/{database}"
                    )
                elif db_backend == "sqlite":
                    cfg["connection_string"] = f"sqlite:///./{db_name}.db"
                else:
                    cfg["connection_string"] = (
                        "postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}"
                    )

                with db_config_path.open("w") as f:
                    json.dump(cfg, f, indent=4)
            except Exception:
                # If anything goes wrong here, leave the template as-is.
                pass

        # Update app.py title/description to use the project name without FastMVC branding
        app_path = self.project_path / "app.py"
        if app_path.exists():
            content = app_path.read_text()
            content = content.replace(
                'title="FastMVC API"',
                f'title="{self.project_name.replace("_", " ").title()} API"'
            )
            content = content.replace(
                'description="Production-grade FastAPI application with MVC architecture"',
                f'description="{self.project_name.replace("_", " ").title()} API service"'
            )
            app_path.write_text(content)

    def _init_git(self):
        """Initialize a git repository in the project directory."""
        try:
            subprocess.run(
                ["git", "init"],
                cwd=self.project_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "add", "."],
                cwd=self.project_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=self.project_path,
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            click.secho(
                f"    ⚠ Git initialization failed: {e.stderr.decode() if e.stderr else str(e)}",
                fg="yellow"
            )
        except FileNotFoundError:
            click.secho("    ⚠ Git not found. Skipping repository initialization.", fg="yellow")

    def _create_venv(self):
        """Create a Python virtual environment."""
        venv_path = self.project_path / "venv"
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            click.secho(
                f"    ⚠ Virtual environment creation failed: {e}",
                fg="yellow"
            )

    def _install_deps(self):
        """Install project dependencies."""
        requirements_path = self.project_path / "requirements.txt"
        if not requirements_path.exists():
            click.secho("    ⚠ requirements.txt not found.", fg="yellow")
            return

        # Determine pip path
        if self.create_venv:
            if sys.platform == "win32":
                pip_path = self.project_path / "venv" / "Scripts" / "pip"
            else:
                pip_path = self.project_path / "venv" / "bin" / "pip"
        else:
            pip_path = "pip"

        try:
            subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_path)],
                cwd=self.project_path,
                check=True
            )
        except subprocess.CalledProcessError as e:
            click.secho(
                f"    ⚠ Dependency installation failed: {e}",
                fg="yellow"
            )

