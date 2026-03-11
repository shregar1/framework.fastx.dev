# Configurations

## Overview

The `configurations` module provides centralized configuration management for the FastMVC application. It handles loading, validating, and exposing configuration settings for database connections, cache systems, and security features.

## Purpose

In software engineering, **configuration management** is critical for:

- **Environment flexibility**: Different settings for development, staging, and production
- **Security**: Sensitive credentials stored outside of code
- **Maintainability**: Centralized location for all settings
- **Runtime flexibility**: Support for environment variable overrides

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Code                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Configuration Classes                       │
│     (DBConfiguration, CacheConfiguration, etc.)              │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│    JSON Config Files    │     │   Environment Variables     │
│  (config/**/config.json)│     │   (override JSON values)    │
└─────────────────────────┘     └─────────────────────────────┘
```

## Components

### DBConfiguration (`db.py`)

Singleton configuration manager for PostgreSQL database settings.

```python
from configurations.db import DBConfiguration

# Get database configuration
db_config = DBConfiguration()
dto = db_config.get_config()

# Use in SQLAlchemy
from sqlalchemy import create_engine
engine = create_engine(dto.connection_string)
```

**Configuration File**: `config/db/config.json`
```json
{
    "user_name": "postgres",
    "password": "your-password",
    "host": "localhost",
    "port": 5432,
    "database": "fastmvc_db",
    "connection_string": "postgresql://postgres:password@localhost:5432/fastmvc_db"
}
```

### CacheConfiguration (`cache.py`)

Singleton configuration manager for Redis cache settings.

```python
from configurations.cache import CacheConfiguration

# Get cache configuration
cache_config = CacheConfiguration()
dto = cache_config.get_config()

# Use with Redis client
import redis
client = redis.Redis(
    host=dto.host,
    port=dto.port,
    password=dto.password
)
```

**Configuration File**: `config/cache/config.json`
```json
{
    "host": "localhost",
    "port": 6379,
    "password": "your-redis-password"
}
```

### SecurityConfiguration (`security.py`)

Configuration manager for security settings with environment variable override support.

```python
from configurations.security import SecurityConfiguration

# Get security configuration
security_config = SecurityConfiguration()
dto = security_config.get_config()

# Access nested settings
jwt_expiry = dto.authentication.jwt_expiry_minutes
max_attempts = dto.authentication.max_login_attempts

# Hot-reload configuration
new_config = security_config.reload_config()
```

**Configuration File**: `config/security/config.json`
```json
{
    "security_headers": {
        "hsts_max_age": 31536000,
        "hsts_include_subdomains": true,
        "enable_csp": true,
        "enable_hsts": true
    },
    "input_validation": {
        "max_string_length": 1000,
        "min_password_length": 8
    },
    "authentication": {
        "jwt_expiry_minutes": 60,
        "max_login_attempts": 5
    }
}
```

**Environment Variable Overrides**:
| Variable | Section | Key |
|----------|---------|-----|
| `SECURITY_HSTS_MAX_AGE` | security_headers | hsts_max_age |
| `SECURITY_HSTS_INCLUDE_SUBDOMAINS` | security_headers | hsts_include_subdomains |
| `SECURITY_ENABLE_CSP` | security_headers | enable_csp |
| `SECURITY_ENABLE_HSTS` | security_headers | enable_hsts |
| `SECURITY_MAX_STRING_LENGTH` | input_validation | max_string_length |
| `SECURITY_MIN_PASSWORD_LENGTH` | input_validation | min_password_length |
| `SECURITY_JWT_EXPIRY_MINUTES` | authentication | jwt_expiry_minutes |
| `SECURITY_MAX_LOGIN_ATTEMPTS` | authentication | max_login_attempts |

## Design Patterns

### Singleton Pattern (DB & Cache)

Database and cache configurations use the Singleton pattern to ensure:
- Single source of truth for configuration
- One-time file loading
- Memory efficiency

```python
# Both return the same instance
config1 = DBConfiguration()
config2 = DBConfiguration()
assert config1 is config2  # True
```

### DTO Pattern

All configuration classes return Pydantic DTOs for:
- Type validation
- IDE autocompletion
- Serialization support

## File Structure

```
configurations/
├── __init__.py         # Package exports
├── cache.py           # Redis cache configuration
├── db.py              # Database configuration
├── security.py        # Security settings configuration
└── README.md          # This documentation

config/
├── cache/
│   └── config.json    # Cache settings
├── db/
│   └── config.json    # Database settings
└── security/
    └── config.json    # Security settings
```

## Best Practices

1. **Never commit secrets**: Add `config/` to `.gitignore`
2. **Use environment variables in production**: Override sensitive values
3. **Provide sensible defaults**: Fallback values in `constants/default.py`
4. **Validate early**: Configuration is loaded and validated at startup
5. **Log configuration loading**: Debug logs help troubleshoot issues

## Error Handling

All configuration classes handle errors gracefully:
- Missing files: Logged, defaults used
- Invalid JSON: Logged, defaults used
- Missing keys: DTO validation catches issues

```python
# Even if config file is missing, this won't crash
config = DBConfiguration().get_config()
# Will use empty/default values
```
