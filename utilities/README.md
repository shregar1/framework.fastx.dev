# Utilities

## Overview

The `utilities` module provides helper classes and functions for common operations across the FastMVC application. Utilities handle cross-cutting concerns like validation, data transformation, and authentication.

## Purpose

**Utilities** provide:

- **Reusability**: Common logic in one place
- **Consistency**: Standardized operations across the app
- **Security**: Validation and sanitization
- **Transformation**: Data format conversion

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            Controllers / Services / DTOs                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Utilities                               │
│   (DictionaryUtility, JWTUtility, ValidationUtility)         │
└─────────────────────────────────────────────────────────────┘
```

## Components

### DictionaryUtility (`dictionary.py`)

Operations for dictionary manipulation and key transformation.

```python
from utilities.dictionary import DictionaryUtility

util = DictionaryUtility(urn="urn:req:123", ...)

# Convert snake_case to camelCase (for API responses)
response = util.convert_dict_keys_to_camel_case({
    "user_name": "John",
    "last_login": "2024-01-15"
})
# Result: {"userName": "John", "lastLogin": "2024-01-15"}

# Convert camelCase to snake_case (for internal use)
data = util.convert_dict_keys_to_snake_case({
    "userName": "John"
})
# Result: {"user_name": "John"}

# Mask sensitive values
masked = util.mask_dict_values({"password": "secret123"})
# Result: {"password": "XXXXXXXXX"}

# Remove keys
cleaned = util.remove_keys_from_dict(data, ["password", "token"])
```

**Methods:**

| Method | Description |
|--------|-------------|
| `snake_to_camel_case` | Convert single string |
| `camel_to_snake_case` | Convert single string |
| `convert_dict_keys_to_camel_case` | Recursive dict conversion |
| `convert_dict_keys_to_snake_case` | Recursive dict conversion |
| `mask_value` | Mask a single value |
| `mask_dict_values` | Recursive value masking |
| `remove_keys_from_dict` | Remove specified keys |
| `build_dictonary_with_key` | Build dict from list of objects |

### JWTUtility (`jwt.py`)

JWT token creation and validation.

```python
from utilities.jwt import JWTUtility

jwt_util = JWTUtility(urn="urn:req:123", ...)

# Create access token
token = jwt_util.create_access_token({
    "user_id": 123,
    "user_urn": "urn:user:abc"
})
# Result: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Decode token
payload = jwt_util.decode_token(token)
# Result: {"user_id": 123, "user_urn": "urn:user:abc", "exp": ...}
```

**Methods:**

| Method | Description |
|--------|-------------|
| `create_access_token(data)` | Create JWT with expiration |
| `decode_token(token)` | Decode and validate JWT |

**Configuration (from start_utils):**
- `SECRET_KEY`: JWT signing secret
- `ALGORITHM`: Signing algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token validity duration

### ValidationUtility (`validation.py`)

Input validation and sanitization.

```python
from utilities.validation import ValidationUtility, SecurityValidators

# Password validation
result = ValidationUtility.validate_password_strength("MyP@ss123")
# Result: {"is_valid": True, "issues": []}

result = ValidationUtility.validate_password_strength("weak")
# Result: {"is_valid": False, "issues": ["Password must be at least 8 characters..."]}

# Email validation
result = ValidationUtility.validate_email_format("user@example.com")
# Result: {"is_valid": True, "normalized_email": "user@example.com"}

# UUID validation
is_valid = ValidationUtility.validate_uuid_format("550e8400-e29b-41d4-a716-446655440000")
# Result: True

# String sanitization
clean = ValidationUtility.sanitize_string("  hello\x00world  ")
# Result: "hello world"

# Security checks
is_safe = SecurityValidators.validate_sql_injection_prevention(user_input)
is_safe = SecurityValidators.validate_xss_prevention(user_input)
is_safe = SecurityValidators.validate_path_traversal_prevention(user_input)
```

**ValidationUtility Methods:**

| Method | Description |
|--------|-------------|
| `validate_password_strength` | Check password complexity |
| `validate_email_format` | Validate and normalize email |
| `validate_uuid_format` | Check valid UUID |
| `validate_date_range` | Check date range validity |
| `sanitize_string` | Remove dangerous characters |
| `validate_numeric_range` | Check number in range |
| `validate_string_length` | Check string length |

**SecurityValidators Methods:**

| Method | Description |
|--------|-------------|
| `validate_sql_injection_prevention` | Detect SQL injection |
| `validate_xss_prevention` | Detect XSS attacks |
| `validate_path_traversal_prevention` | Detect path traversal |

## Password Requirements

The `validate_password_strength` method enforces:

| Requirement | Description |
|-------------|-------------|
| Length | At least 8 characters |
| Lowercase | At least one (a-z) |
| Uppercase | At least one (A-Z) |
| Digit | At least one (0-9) |
| Special | At least one of @$!%*?& |
| No repeats | No 3+ consecutive identical characters |
| Not common | Not in weak password list |

### CacheUtility (`cache.py`)

Redis-based caching with decorators for function result caching.

```python
from utilities.cache import CacheUtility, create_cache
from start_utils import redis_session

# Create cache instance
cache = create_cache(redis_session, default_ttl=3600)

# Cache function results with decorator
@cache.cached(ttl=300, prefix="user")
async def get_user(user_id: int):
    return await db.fetch_user(user_id)

# With custom key function
@cache.cached(key_func=lambda uid: f"profile:{uid}")
async def get_profile(user_id: int):
    return await db.fetch_profile(user_id)

# Invalidate cache after modifications
@cache.invalidate("user:*")
async def update_user(user_id: int, data: dict):
    return await db.update_user(user_id, data)

# Manual cache operations
cache.set("my_key", {"data": "value"}, ttl=300)
data = cache.get("my_key")
cache.delete("my_key")
cache.delete_pattern("user:*")
cache.clear()  # Clear all cached values with prefix
```

**Methods:**

| Method | Description |
|--------|-------------|
| `get(key)` | Retrieve value from cache |
| `set(key, value, ttl)` | Store value with optional TTL |
| `delete(key)` | Remove single key |
| `delete_pattern(pattern)` | Remove keys matching pattern |
| `clear()` | Clear all cached values |
| `cached(ttl, prefix, key_func)` | Decorator for caching results |
| `invalidate(prefix)` | Decorator for cache invalidation |

**Features:**
- Automatic key generation from function arguments
- Support for both sync and async functions
- Pattern-based cache invalidation
- Pickle serialization for complex objects
- Graceful degradation when Redis is unavailable

## File Structure

```
utilities/
├── __init__.py
├── README.md
├── cache.py           # Redis caching with decorators
├── dictionary.py      # Dictionary manipulation
├── jwt.py             # JWT token operations
└── validation.py      # Input validation and security
```

## Usage with Dependencies

Utilities are typically injected via dependency factories:

```python
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency

class MyController:
    async def post(
        self,
        dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
        jwt_utility: JWTUtility = Depends(JWTUtilityDependency.derive)
    ):
        util = dictionary_utility(urn=self.urn, ...)
        jwt = jwt_utility(urn=self.urn, ...)
```

## Best Practices

1. **Use factories for DI**: Pass request context (URN)
2. **Log operations**: Debug logging for troubleshooting
3. **Validate early**: Check input at API boundary
4. **Sanitize strings**: Before storage or display
5. **Never log sensitive data**: Passwords, tokens
6. **Use static methods for stateless operations**: Validation methods

## Adding New Utilities

1. Create new file in `utilities/` directory
2. Inherit from `IUtility` if stateful
3. Use static methods for stateless operations
4. Add comprehensive docstrings
5. Create corresponding dependency in `dependencies/utilities/`
6. Update this README
