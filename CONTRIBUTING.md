# Contributing to FastMVC

Thank you for your interest in contributing to FastMVC! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Be kind, constructive, and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Docker (for running tests with PostgreSQL/Redis)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/shregar1/fastMVC.git
   cd fastmvc
   ```

3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/shregar1/fastMVC.git
   ```

## Development Setup

### Using uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager. Install it first:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then set up the project:

```bash
# Install dependencies and create virtual environment
uv sync --all-extras

# Start infrastructure
docker-compose up -d postgres redis

# Run tests
uv run pytest tests/ -v

# Run the CLI
uv run fastmvc version
```

### Using pip (Alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Start infrastructure
docker-compose up -d postgres redis

# Verify installation
fastmvc version
pytest tests/ -v
```

## Making Changes

### Branch Naming

Create a descriptive branch for your changes:

```bash
# For features
git checkout -b feature/add-websocket-support

# For bug fixes
git checkout -b fix/rate-limiter-memory-leak

# For documentation
git checkout -b docs/improve-readme

# For refactoring
git checkout -b refactor/simplify-middleware
```

### Commit Messages

Follow the conventional commits specification:

```
type(scope): brief description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(cli): add entity generator command
fix(auth): handle expired token gracefully
docs(readme): add CLI usage examples
test(services): add user registration tests
```

## Branch Protection Policy

⚠️ **Direct pushes to `main` are disabled.** All changes must go through a Pull Request.

This ensures:
- Code review before merging
- CI tests pass on all changes
- Changelog and documentation are updated
- Code quality is maintained

See `.github/BRANCH_PROTECTION.md` for setup instructions.

## Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests and linting**:
   ```bash
   pytest tests/ -v --cov
   black .
   isort .
   ruff check .
   mypy .
   ```

3. **Push your changes**:
   ```bash
   git push origin your-branch-name
   ```

4. **Create Pull Request**:
   - Go to GitHub and create a PR from your fork
   - Fill in the PR template
   - Link any related issues

5. **PR Requirements**:
   - All tests pass
   - Code coverage maintained or improved
   - Documentation updated if needed
   - No linting errors
   - Approved by at least one maintainer

## Coding Standards

### Python Style

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Use type hints for all function parameters and returns
- Use docstrings for all public functions, classes, and modules

### Code Formatting

```bash
# Format code
black .

# Sort imports
isort .

# Check for issues
ruff check .

# Type checking
mypy .
```

### Docstrings

Use Google-style docstrings:

```python
def create_user(email: str, password: str) -> User:
    """
    Create a new user account.
    
    Args:
        email: User's email address.
        password: User's password (will be hashed).
    
    Returns:
        Created User instance.
    
    Raises:
        BadInputError: If email already exists.
    
    Example:
        >>> user = create_user("user@example.com", "SecureP@ss1")
        >>> print(user.email)
        user@example.com
    """
    pass
```

### File Structure

When adding new features:

1. **Model**: `models/<entity>.py`
2. **Repository**: `repositories/<entity>.py`
3. **Service**: `services/<entity>/<operation>.py`
4. **Controller**: `controllers/<entity>/<operation>.py`
5. **DTOs**: `dtos/requests/<entity>/` and `dtos/responses/<entity>/`
6. **Tests**: `tests/unit/<layer>/test_<entity>.py`

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/services/test_user_services.py -v

# Run tests matching pattern
pytest -k "test_login" -v
```

### Writing Tests

- Use `pytest` fixtures for setup
- Mock external dependencies
- Test both success and error cases
- Aim for >80% code coverage

```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    """Tests for UserService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return Mock()
    
    def test_create_user_success(self, mock_repository):
        """Test successful user creation."""
        # Arrange
        mock_repository.create_record.return_value = User(id=1, email="test@example.com")
        service = UserService(repository=mock_repository)
        
        # Act
        result = service.create(email="test@example.com", password="SecureP@ss1")
        
        # Assert
        assert result.email == "test@example.com"
        mock_repository.create_record.assert_called_once()
    
    def test_create_user_duplicate_email(self, mock_repository):
        """Test user creation with duplicate email."""
        # Arrange
        mock_repository.retrieve_record_by_email.return_value = User(id=1)
        service = UserService(repository=mock_repository)
        
        # Act & Assert
        with pytest.raises(BadInputError):
            service.create(email="existing@example.com", password="SecureP@ss1")
```

## Documentation

### README Files

Each module should have a README.md with:

- Overview/Purpose
- Usage examples
- API reference
- Configuration options

### Code Comments

- Use comments for complex logic
- Explain "why", not "what"
- Keep comments up to date with code changes

### Changelog

Update CHANGELOG.md for user-facing changes:

```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description
```

## Questions?

If you have questions:

1. Check existing issues and documentation
2. Open a GitHub issue with the "question" label
3. Join our Discord community (coming soon)

Thank you for contributing to FastMVC! 🎉

