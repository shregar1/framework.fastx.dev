# Testing Guide

FastMVC provides a comprehensive testing framework with factories, fixtures, and utilities for testing your application.

## Installation

Install testing dependencies:

```bash
pip install pytest pytest-asyncio httpx faker freezegun
```

Or use the provided requirements:

```bash
pip install -r requirements-dev.txt
```

## Test Structure

The **`tests/`** tree **mirrors** the application layout (controllers, services, dtos, factories, middlewares, repositories, etc.). Put each test module next to the same path as the code under test (for example, `tests/example/test_example_item.py` for Item API tests, `tests/factories/apis/v1/example/` for DTO factory tests).

```text
my-project/
├── tests/
│   ├── conftest.py                    # Shared fixtures
│   ├── example/
│   │   └── test_example_item.py       # Item API tests (legacy path)
│   ├── factories/apis/v1/example/
│   │   └── test_factories_example.py
│   └── …                              # abstractions, controllers, services, …
└── testing/item/                      # ItemFactory + pytest fixtures (imported by conftest)
    ├── factories.py
    └── fixtures.py
```

## Factories

Factories generate fake test data using `faker`.

DTOs in `dtos/requests/<segment>/` follow **one concrete Pydantic class per module** (nested helpers may share a file with their parent). Factory modules should import the matching DTO from the same paths (e.g. `dtos.requests.example.create`). See [New API scaffolding — One concrete class per file](new-api-scaffolding.md#one-concrete-class-per-file-dtos).

### ItemFactory

```python
from testing.item import ItemFactory

# Create single entity
item = ItemFactory.create(name="Custom Name")

# Create multiple entities
items = ItemFactory.create_batch(5)

# Create API payload
payload = ItemFactory.create_dict(completed=True)

# Create with specific state
completed = ItemFactory.completed()
pending = ItemFactory.pending()

# Boundary testing
long_name_item = ItemFactory.with_long_name()
```

### Factory Methods

| Method | Description |
|--------|-------------|
| `create(**overrides)` | Create Item |
| `create_batch(n)` | Create n items |
| `create_dict()` | Create API payload dict |
| `completed()` | Create completed item |
| `pending()` | Create pending item |
| `with_long_name()` | Create with max length name |
| `invalid_name_empty()` | Invalid payload for testing |

## Fixtures

Fixtures are automatically available in tests via `conftest.py`.

### DataI Fixtures

```python
def test_with_db(item_db, item_repository):
    """Use in-memory database."""
    # item_db: Dict-Id in-memory database
    # item_repository: Mocked repository
    pass
```

### Client Fixtures

```python
def test_endpoint(item_client):
    """Use FastAPI test client."""
    response = item_client.get("/items")
    assert response.status_code == 200

async def test_async(async_item_client):
    """Use async HTTPX client."""
    response = await async_item_client.get("/items")
    assert response.status_code == 200
```

### Auth Fixtures

```python
def test_with_auth(item_client, mock_auth, mock_user):
    """Test with mocked authentication."""
    with mock_auth:
        response = item_client.get("/items")
        assert response.status_code == 200

def test_invalid_auth(item_client, mock_invalid_auth):
    """Test with invalid auth."""
    with mock_invalid_auth:
        response = item_client.get("/items")
        assert response.status_code == 401
```

### Test Data Fixtures

```python
def test_with_item(item_client, test_item, mock_auth):
    """Single test item provided."""
    with mock_auth:
        response = item_client.get(f"/items/{test_item.id}")
        assert response.json()["name"] == test_item.name

def test_with_items(item_client, test_items, mock_auth):
    """Multiple test items provided."""
    with mock_auth:
        response = item_client.get("/items")
        assert len(response.json()["items"]) == 5
```

## Writing Tests

### Basic Test Structure

```python
import pytest

# Optional: Mark all tests in file
pytestmark = [pytest.mark.api, pytest.mark.integration]

class TestItemCreate:
    """Group related tests in classes."""
    
    def test_create_success(self, item_client, create_item_payload):
        """Descriptive test name."""
        response = item_client.post("/items", json=create_item_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == create_item_payload["name"]
    
    def test_create_validation_error(self, item_client):
        """Test validation errors."""
        response = item_client.post("/items", json={"name": ""})
        
        assert response.status_code == 422
```

### Using Markers

```python
@pytest.mark.unit
def test_unit_test():
    """Fast unit test."""
    pass

@pytest.mark.slow
def test_slow_test():
    """Slow test skipped in fast mode."""
    pass

@pytest.mark.parametrize("name,expected", [
    ("Item 1", 201),
    ("", 422),
])
def test_parametrized(name, expected):
    """Run test with multiple inputs."""
    pass
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_endpoint(async_item_client):
    """Test async endpoint."""
    response = await async_item_client.get("/items")
    assert response.status_code == 200
```

## Running Tests

### Run All Tests

```bash
# Using pytest directly
pytest

# Using make
make test

# Verbose output
pytest -v

# With coverage
pytest --cov=. --cov-report=html
```

### Run Specific Tests

```bash
# Run specific file
pytest tests/example/test_example_item.py

# Run specific test class
pytest tests/example/test_example_item.py::TestItemCreate

# Run specific test method
pytest tests/example/test_example_item.py::TestItemCreate::test_create_item_success

# Run by marker
pytest -m unit          # Only unit tests
pytest -m "not slow"    # Skip slow tests
pytest -m api           # Only API tests
```

### Run with VS Code

Use the built-in test explorer or debug configuration:

1. Open Testing panel (beaker icon)
2. Click play button on test/class/file
3. Or press `F5` to debug

## Test Categories

### Unit Tests

Test individual components in isolation:

```python
@pytest.mark.unit
def test_entity_validation():
    """Test entity validation logic."""
    from models.item import Item
    
    with pytest.raises(ValueError):
        Item(name="")  # Empty name should fail
```

### Integration Tests

Test component interactions:

```python
@pytest.mark.integration
def test_create_and_get(item_client, mock_auth):
    """Test create then get flow."""
    with mock_auth:
        # Create
        create_resp = item_client.post("/items", json={
            "name": "Integration Test"
        })
        item_id = create_resp.json()["id"]
        
        # Get
        get_resp = item_client.get(f"/items/{item_id}")
        assert get_resp.json()["name"] == "Integration Test"
```

### End-to-End Tests

Test complete user flows:

```python
@pytest.mark.e2e
def test_full_item_lifecycle(item_client, mock_auth):
    """Test complete CRUD flow."""
    with mock_auth:
        # Create
        # Read
        # Update
        # Delete
        pass
```

## Mocking

### Mock External Services

```python
from unittest.mock import patch, Mock

def test_with_mocked_email():
    """Mock email service."""
    with patch("services.email.send") as mock_send:
        mock_send.return_value = Mock(success=True)
        
        # Run code that sends email
        
        mock_send.assert_called_once()
```

### Mock Time

```python
def test_timestamp(freezer):
    """Freeze time for deterministic tests."""
    freezer.move_to("2024-01-01")
    
    item = ItemFactory.create()
    assert item.created_at.year == 2024
```

## Best Practices

1. **Use descriptive names**: `test_create_item_with_empty_name_returns_422`
2. **One assertion concept per test**: Don't test 5 things in one test
3. **Use fixtures for setup**: Avoid repeating setup code
4. **Clean up after tests**: Use fixtures for cleanup
5. **Test edge cases**: Empty strings, max lengths, null values
6. **Use markers**: Organize tests by type/speed
7. **Parametrize when possible**: Test multiple inputs efficiently

## Troubleshooting

### Import Errors

Ensure `conftest.py` is in the tests directory and adds project root to path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### DataI Locked (SQLite)

Use `:memory:` database or ensure proper cleanup:

```python
@pytest.fixture
def db():
    db = create_engine("sqlite:///:memory:")
    yield db
    db.dispose()
```

### Async Fixtures Not Working

Ensure `pytest-asyncio` is installed and configured:

```python
# conftest.py
pytest_plugins = ("pytest_asyncio",)
```

## VS Code Integration

The `.vscode/` folder includes:

- **Test discovery**: Automatically find tests
- **Debug configurations**: Debug individual tests
- **Task shortcuts**: Run tests from command palette

Shortcuts:

- `Cmd+Shift+T` - Run tests
- `F5` - Debug test at cursor
- Click play button in test explorer
