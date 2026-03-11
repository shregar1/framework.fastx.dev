# FastMVC CLI

Command-line interface for the FastMVC framework.

## Installation

```bash
# From PyPI (when published)
pip install fastmvc

# From source
cd fastmvc
pip install -e .
```

## Usage

### Generate a New Project

```bash
fastmvc generate my_project
```

This creates a new FastAPI project with the complete FastMVC architecture:

```
my_project/
├── abstractions/       # Base interfaces
├── config/             # JSON configs
├── configurations/     # Config loaders
├── constants/          # App constants
├── controllers/        # Route handlers
├── dependencies/       # DI factories
├── dtos/               # Data transfer objects
├── errors/             # Custom exceptions
├── middlewares/        # Middleware stack
├── models/             # SQLAlchemy models
├── repositories/       # Data access layer
├── services/           # Business logic
├── tests/              # Test suite
├── utilities/          # Helpers
├── app.py              # FastAPI app
├── docker-compose.yml  # Docker services
├── Dockerfile          # Container build
├── requirements.txt    # Dependencies
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # Project docs
```

### Options

```bash
# Create project in a specific directory
fastmvc generate my_project --output-dir ~/projects

# Skip git initialization
fastmvc generate my_project --no-git

# Create with virtual environment
fastmvc generate my_project --venv

# Create and install dependencies
fastmvc generate my_project --venv --install
```

### Other Commands

```bash
# Show version
fastmvc version

# Show framework info
fastmvc info

# Show help
fastmvc --help
fastmvc generate --help
```

## Development

### Running Locally

```bash
# Install in development mode
pip install -e .

# Test the CLI
fastmvc --help
fastmvc generate test_project
```

### Testing

```bash
pytest tests/ -v
```

## Architecture

The CLI is built with [Click](https://click.palletsprojects.com/), a Python package for creating beautiful command-line interfaces.

### Module Structure

- `__init__.py` - Package initialization with version info
- `cli.py` - Click command definitions
- `generator.py` - Project generation logic

## License

MIT License

