# FastMVC Test Suite

Comprehensive test suite for the FastMVC framework with 100% code coverage target.

## Overview

This test suite covers all major components of the FastMVC framework:

- **Utilities**: Dictionary manipulation, JWT operations, validation
- **DTOs**: Request/response data transfer objects
- **Errors**: Custom exception classes
- **Constants**: Application constants and configuration values
- **Abstractions**: Base classes and interfaces
- **Models**: SQLAlchemy ORM models
- **Repositories**: Data access layer
- **Services**: Business logic layer
- **Controllers**: HTTP request handlers
- **Middlewares**: Request/response middleware
- **Dependencies**: FastAPI dependency injection
- **Configurations**: Configuration loaders
- **App**: Main application

## Running Tests

### All Tests with Coverage

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/unit/utilities/test_dictionary.py
```

### Run Specific Test Class

```bash
pytest tests/unit/utilities/test_dictionary.py::TestDictionaryUtility
```

### Run Specific Test

```bash
pytest tests/unit/utilities/test_dictionary.py::TestDictionaryUtility::test_snake_to_camel_case_simple
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

### Run Only Unit Tests

```bash
pytest tests/unit/
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── README.md
├── test_app.py                  # Application tests
└── unit/
    ├── __init__.py
    ├── abstractions/
    │   ├── __init__.py
    │   └── test_abstractions.py
    ├── configurations/
    │   ├── __init__.py
    │   └── test_configurations.py
    ├── constants/
    │   ├── __init__.py
    │   └── test_constants.py
    ├── controllers/
    │   ├── __init__.py
    │   └── test_user_controllers.py
    ├── dependencies/
    │   ├── __init__.py
    │   └── test_dependencies.py
    ├── dtos/
    │   ├── __init__.py
    │   ├── test_base.py
    │   ├── test_requests.py
    │   └── test_responses.py
    ├── errors/
    │   ├── __init__.py
    │   └── test_errors.py
    ├── middlewares/
    │   ├── __init__.py
    │   └── test_middlewares.py
    ├── models/
    │   ├── __init__.py
    │   └── test_user.py
    ├── repositories/
    │   ├── __init__.py
    │   └── test_user.py
    ├── services/
    │   ├── __init__.py
    │   └── test_user_services.py
    └── utilities/
        ├── __init__.py
        ├── test_dictionary.py
        ├── test_jwt.py
        └── test_validation.py
```

## Fixtures

Common fixtures are defined in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `sample_user_data` | Sample user data dictionary |
| `valid_uuid` | Valid UUID string |
| `mock_db_session` | Mock SQLAlchemy session |
| `mock_redis_session` | Mock Redis session |
| `mock_user` | Mock user object |
| `mock_request` | Mock FastAPI request |
| `valid_password` | Valid password meeting requirements |
| `valid_email` | Valid email address |
| `test_urn` | Test URN string |
| `jwt_payload` | Sample JWT payload |
| `mock_async_call_next` | Mock async middleware call_next |

## Coverage Configuration

Coverage is configured in `.coveragerc`:

- Source includes all project files
- Tests and virtual environments are excluded
- Minimum coverage threshold: 80%
- HTML report generated in `htmlcov/`

## Writing New Tests

### Unit Test Template

```python
"""
Tests for MyClass.
"""

import pytest
from module.path import MyClass


class TestMyClass:
    """Tests for MyClass."""

    @pytest.fixture
    def instance(self):
        """Create MyClass instance."""
        return MyClass()

    def test_method_name(self, instance):
        """Test description."""
        result = instance.method()
        assert result == expected_value

    @pytest.mark.asyncio
    async def test_async_method(self, instance):
        """Test async method."""
        result = await instance.async_method()
        assert result is not None
```

### Best Practices

1. **One assertion per test** when possible
2. **Descriptive test names**: `test_method_returns_expected_when_condition`
3. **Use fixtures** for common setup
4. **Mock external dependencies**: database, cache, APIs
5. **Test edge cases**: empty inputs, None values, errors
6. **Group related tests** in classes

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Debugging Failed Tests

### Run with print output

```bash
pytest -v -s
```

### Run with debugger

```bash
pytest --pdb
```

### Run only failed tests

```bash
pytest --lf
```

