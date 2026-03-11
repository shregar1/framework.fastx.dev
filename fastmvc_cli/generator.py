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
        return sanitized or "fastmvc_project"

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

        # Create .gitignore
        self._step("Creating .gitignore")
        self._create_gitignore()

        # Create project README
        self._step("Creating README.md")
        self._create_readme()

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

    def _create_env_example(self):
        """Create the .env.example file with default configuration."""
        env_content = f"""# {self.project_name.upper()} Environment Configuration
# Copy this file to .env and update with your values

# Application Settings
APP_NAME="{self.project_name}"
APP_ENV="development"
APP_DEBUG="true"
APP_HOST="0.0.0.0"
APP_PORT="8000"

# Database Configuration
DATABASE_HOST="localhost"
DATABASE_PORT="5432"
DATABASE_NAME="{self.project_name}"
DATABASE_USER="postgres"
DATABASE_PASSWORD="postgres123"
DATABASE_POOL_SIZE="5"
DATABASE_MAX_OVERFLOW="10"

# Redis Configuration
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD="test123"
REDIS_DB="0"

# Security Settings
JWT_SECRET_KEY="your-super-secret-jwt-key-change-this-in-production"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS="24"
BCRYPT_SALT="$2b$12$LQv3c1yqBWVHxkd0LHAkCO"

# CORS Settings
CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
CORS_ALLOW_CREDENTIALS="true"
CORS_ALLOW_METHODS="GET,POST,PUT,DELETE,OPTIONS,PATCH"
CORS_ALLOW_HEADERS="*"

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE="60"
RATE_LIMIT_REQUESTS_PER_HOUR="1000"
RATE_LIMIT_BURST_LIMIT="10"

# Logging
LOG_LEVEL="DEBUG"
LOG_FORMAT="json"
"""
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
        readme_content = f"""<div align="center">

# 🚀 {project_title}

### Production-Ready API built with FastMVC

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## ⚡ Quick Start

### 1️⃣ Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### 2️⃣ Start Infrastructure

```bash
# Start PostgreSQL + Redis
docker-compose up -d

# Run database migrations
fastmvc migrate upgrade
```

### 3️⃣ Run the Server

```bash
python -m uvicorn app:app --reload
```

### 4️⃣ Done! 🎉

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         HTTP Request                            │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  🛡️ MIDDLEWARE STACK (fastmiddleware - 90+ components)         │
│  RequestContext → Timing → RateLimit → Auth → Security         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  🎮 CONTROLLER → 🔧 SERVICE → 🗄️ REPOSITORY → 💾 DATABASE       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
{self.project_name}/
├── 🎯 app.py                 # FastAPI entry point
├── ⚙️ start_utils.py         # Startup configuration
│
├── 📋 abstractions/          # Base interfaces & contracts
├── 🎮 controllers/           # HTTP route handlers
├── 🔧 services/              # Business logic layer
├── 🗄️ repositories/          # Data access layer
├── 📊 models/                # SQLAlchemy ORM models
├── 📨 dtos/                  # Data Transfer Objects
├── 🛡️ middlewares/           # Request processing
├── 🔄 migrations/            # Alembic migrations
├── 🧪 tests/                 # Test suite
│
└── 🐳 docker-compose.yml     # PostgreSQL + Redis
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | ❌ |
| POST | `/user/register` | User registration | ❌ |
| POST | `/user/login` | User authentication | ❌ |
| POST | `/user/logout` | Session termination | ✅ |
| GET | `/docs` | Swagger UI | ❌ |

---

## 🛠️ CLI Commands

### Add New Entity

```bash
# Generate complete CRUD for an entity
fastmvc add entity Product

# Creates: model, repository, service, controller, DTOs, tests
```

### Database Migrations

```bash
fastmvc migrate generate "add product table"  # Create migration
fastmvc migrate upgrade                        # Apply migrations
fastmvc migrate downgrade                      # Rollback
fastmvc migrate status                         # Show status
```

---

## 🛡️ Middleware Stack

This project uses [**fastmvc-middleware**](https://pypi.org/project/fastmvc-middleware/) with 90+ production-ready components:

```python
from fastmiddleware import (
    SecurityHeadersMiddleware,    # CSP, HSTS, X-Frame-Options
    RateLimitMiddleware,          # Sliding window rate limiting
    RequestContextMiddleware,     # Request tracking & URN
    TimingMiddleware,             # Response time headers
    LoggingMiddleware,            # Structured request logging
)
```

---

## 🔐 Security Features

| Feature | Description |
|---------|-------------|
| 🔑 JWT Authentication | Secure token-based auth |
| 🔒 Password Hashing | Bcrypt with salt |
| 🚦 Rate Limiting | Sliding window (60/min, 1000/hr) |
| 🛡️ Security Headers | CSP, HSTS, X-Frame-Options |
| 📍 Request Tracing | Unique URN per request |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=. --cov-report=html

# Run specific tests
pytest tests/unit/services/ -v
```

---

## 🐳 Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

---

## 📄 License

MIT License - Built with ❤️ using [FastMVC](https://github.com/shregar1/fastMVC)
"""
        readme_path = self.project_path / "README.md"
        readme_path.write_text(readme_content)

    def _customize_configs(self):
        """Update configuration files with the project name."""
        # Update docker-compose.yml
        docker_compose_path = self.project_path / "docker-compose.yml"
        if docker_compose_path.exists():
            content = docker_compose_path.read_text()
            content = content.replace("fastmvc_net", f"{self.project_name}_net")
            content = content.replace("fastmvc:", f"{self.project_name}:")
            content = content.replace('POSTGRES_DB: fastmvc', f'POSTGRES_DB: {self.project_name}')
            docker_compose_path.write_text(content)

        # Update app.py title
        app_path = self.project_path / "app.py"
        if app_path.exists():
            content = app_path.read_text()
            content = content.replace(
                'title="FastMVC API"',
                f'title="{self.project_name.replace("_", " ").title()} API"'
            )
            content = content.replace(
                'description="Production-grade FastAPI application with MVC architecture"',
                f'description="{self.project_name.replace("_", " ").title()} - Built with FastMVC"'
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
                ["git", "commit", "-m", "Initial commit - FastMVC project"],
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

