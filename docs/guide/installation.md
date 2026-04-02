# Installation

## Requirements

- Python 3.10 or higher
- pip or uv package manager

## Install FastX

### Using pip

```bash
pip install fastx-mvc
```

### Using uv (recommended)

```bash
uv pip install fastx-mvc
```

## Verify Installation

```bash
fastx --version
```

## Generate Your First Project

```bash
# Interactive mode
fastx generate

# Or quickstart with defaults
fastx quickstart my-project
```

## Project Dependencies

Generated projects include:

```txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
httpx>=0.26.0
python-dotenv>=1.0.0
structlog>=24.1.0
```

### Optional Dependencies

For database support:

```bash
pip install sqlalchemy alembic asyncpg
```

For Redis caching:

```bash
pip install redis
```

For testing:

```bash
pip install pytest pytest-asyncio pytest-cov
```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/fastx/fastx.git
cd fastx

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```
