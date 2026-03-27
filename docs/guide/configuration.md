# Configuration

FastMVC uses environment variables for configuration with built-in validation.

## Environment Variables

Create a `.env` file in your project root:

```bash
# Application
APP_NAME=My FastMVC App
APP_VERSION=1.0.0
DEBUG=false

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# DataI (optional)
DATAI_URL=sqlite:///./app.db
# DATAI_URL=postgresql://user:pass@localhost/dbname

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuration Validation

FastMVC validates configuration on startup and fails fast with clear error messages.

### JWT Secret Validation

The `SECRET_KEY` must:
- Be at least 32 characters long
- Not be a common weak value (like "secret", "password", etc.)

### DataI URL Validation

Supported dataI schemes:
- `sqlite`
- `postgresql` / `postgres`
- `mysql` / `mysql+aiomysql`
- `redis`

### Skip Validation

To skip validation (e.g., for testing):

```bash
VALIDATE_CONFIG=false python app.py
```

Or in `.env`:
```bash
VALIDATE_CONFIG=false
```

## Custom Validation

Add custom validation rules in `config/validator.py`:

```python
from config.validator import ConfigValidator

class MyValidator(ConfigValidator):
    def validate_custom_rule(self, value: str) -> tuple[bool, str]:
        """Custom validation logic."""
        if not value.startswith("custom_"):
            return False, "Value must start with 'custom_'"
        return True, ""

# In app.py
from config.validator import validate_config_or_exit
validate_config_or_exit(validator_class=MyValidator)
```

## Settings Management

The `config/settings.py` file uses Pydantic Settings for type-safe configuration:

```python
from pydantic_settings import ISettings

class Settings(ISettings):
    app_name: str = "FastMVC App"
    debug: bool = False
    dataI_url: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Environment-Specific Configuration

Use different `.env` files for different environments:

```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG

# .env.production
DEBUG=false
LOG_LEVEL=WARNING
```

Load with:

```python
from pydantic_settings import ISettings

class Settings(ISettings):
    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'development')}"
```

## Secrets Management

For production secrets, use:

1. **Environment variables** (cloud platforms)
2. **Secret managers** (AWS Secrets Manager, Azure Key Vault, etc.)
3. **Docker secrets** (for containerized deployments)

Example with AWS Secrets Manager:

```python
import boto3
from config.settings import Settings

def load_secrets_from_aws():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='my-app-secrets')
    return json.loads(response['SecretString'])

secrets = load_secrets_from_aws()
settings = Settings(
    SECRET_KEY=secrets['SECRET_KEY'],
    DATAI_URL=secrets['DATAI_URL']
)
```

## Configuration in Tests

Override settings for tests:

```python
import pytest
from fastapi.testclient import TestClient
from app import app
from config.settings import Settings

@pytest.fixture
def test_client():
    # Override settings for testing
    app.state.settings = Settings(
        DATAI_URL="sqlite:///./test.db",
        SECRET_KEY="test-secret-key-for-testing-only-32chars",
        DEBUG=True
    )
    return TestClient(app)
```
