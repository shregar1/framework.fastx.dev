# Quick Start

## Create a New Project

### Interactive Mode

```bash
fastmvc generate
```

Follow the prompts to customize your project:

- Project name
- Location
- Author details
- Virtual environment setup
- Pre-commit hooks

### Quick Start Mode

```bash
fastmvc quickstart my-project
```

This creates a project with sensible defaults:

- Project name: `my-project`
- Location: current directory
- Virtual environment: `.venv`
- Pre-commit hooks: enabled

## Run Your Application

```bash
cd my-project

# Install dependencies
make install

# Run development server
make dev
```

Your API will be available at:

- Application: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Example API

Generated projects include a complete Item CRUD example at `/items`:

```bash
# Create an item
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Buy milk", "description": "Get from store"}'

# List items
curl http://localhost:8000/items

# Get specific item
curl http://localhost:8000/items/1

# Update item
curl -X PUT http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Buy organic milk"}'

# Delete item
curl -X DELETE http://localhost:8000/items/1
```

## Project Structure

```text
my-project/
├── app.py                 # Application entry point
├── config/                # Configuration
│   ├── settings.py
│   └── validator.py
├── models/item.py         # Sample Item model (Item)
├── repositories/item.py   # ItemRepository
├── services/item/
├── controllers/apis/v1/item/
├── testing/item/
├── abstractions/          # I classes
├── core/                  # Core utilities
├── middlewares/           # Middleware
├── dtos/                  # Data transfer objects
├── tests/                 # Test suite
├── .vscode/               # VS Code settings
├── docs/                  # Documentation
├── Makefile               # Development commands
└── requirements.txt
```

## Next Steps

- [CLI Reference](cli.md) - Learn about all CLI commands
- [Configuration](configuration.md) - Set up environment variables
- [API Documentation](api-docs.md) - Explore the API docs
- [Project Structure](project-structure.md) - Understand the architecture
