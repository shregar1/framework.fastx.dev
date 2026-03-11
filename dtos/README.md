# Data Transfer Objects (DTOs)

## Overview

The `dtos` module contains Pydantic models for data validation, serialization, and documentation. DTOs ensure type-safe data transfer between layers of the application.

## Purpose

**Data Transfer Objects (DTOs)** provide:

- **Type validation**: Automatic validation of incoming data
- **Serialization**: Convert between Python objects and JSON
- **Documentation**: Self-documenting API contracts
- **Security**: Input sanitization and security validation
- **IDE support**: Autocompletion and type checking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HTTP Request                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Request DTOs                              │
│     (Validation, Sanitization, Type Conversion)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Controller Layer                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Service Layer                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Repository Layer                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DB Model Layer                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Response DTOs                              │
│          (Standardized Response Structure)                   │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Base Models

#### EnhancedBaseModel (`base.py`)

Security-enhanced base model for request DTOs.

```python
from dtos.base import EnhancedBaseModel

class MyRequestDTO(EnhancedBaseModel):
    username: str
    email: str

# Input is automatically sanitized
dto = MyRequestDTO(username="  john  ", email="USER@Example.com")
dto.username  # "john" (trimmed)

# Security validation
result = dto.validate_security()
if not result['is_valid']:
    print(result['issues'])
```

**Features:**
- Automatic string sanitization
- SQL injection detection
- XSS attack detection
- Path traversal detection
- Extra fields rejected

### Request DTOs

#### IRequestDTO (`requests/abstraction.py`)

Base class for all request DTOs.

```python
from dtos.requests.abstraction import IRequestDTO

class MyRequestDTO(IRequestDTO):
    custom_field: str

# Requires valid UUID reference_number
request = MyRequestDTO(
    reference_number="550e8400-e29b-41d4-a716-446655440000",
    custom_field="value"
)
```

#### UserLoginRequestDTO (`requests/user/login.py`)

```python
from dtos.requests.user.login import UserLoginRequestDTO

login = UserLoginRequestDTO(
    reference_number="550e8400-e29b-41d4-a716-446655440000",
    email="user@example.com",
    password="SecureP@ss123"
)
```

**Validation:**
- Email: Valid format, normalized
- Password: Non-empty, meets strength requirements

#### UserRegistrationRequestDTO (`requests/user/registration.py`)

```python
from dtos.requests.user.registration import UserRegistrationRequestDTO

register = UserRegistrationRequestDTO(
    reference_number="550e8400-e29b-41d4-a716-446655440000",
    email="newuser@example.com",
    password="SecureP@ss123"
)
```

#### UserLogoutRequestDTO (`requests/user/logout.py`)

```python
from dtos.requests.user.logout import UserLogoutRequestDTO

logout = UserLogoutRequestDTO(
    reference_number="550e8400-e29b-41d4-a716-446655440000"
)
```

### Response DTOs

#### BaseResponseDTO (`responses/base.py`)

Standard response structure for all endpoints.

```python
from dtos.responses.base import BaseResponseDTO
from constants.api_status import APIStatus

# Success response
response = BaseResponseDTO(
    transactionUrn="urn:req:abc123",
    status=APIStatus.SUCCESS,
    responseMessage="Operation completed",
    responseKey="success_operation",
    data={"result": "value"}
)

# Error response
error_response = BaseResponseDTO(
    transactionUrn="urn:req:abc123",
    status=APIStatus.FAILED,
    responseMessage="Validation failed",
    responseKey="error_validation",
    data={},
    errors=[{"field": "email", "message": "Invalid format"}]
)
```

**JSON Output:**
```json
{
    "transactionUrn": "urn:req:abc123",
    "status": "SUCCESS",
    "responseMessage": "Operation completed",
    "responseKey": "success_operation",
    "data": {"result": "value"},
    "errors": null
}
```

### Configuration DTOs

#### CacheConfigurationDTO (`configurations/cache.py`)

```python
class CacheConfigurationDTO(BaseModel):
    host: str      # Redis host
    port: int      # Redis port
    password: str  # Redis password
```

#### DBConfigurationDTO (`configurations/db.py`)

```python
class DBConfigurationDTO(BaseModel):
    user_name: str
    password: str
    host: str
    port: int
    database: str
    connection_string: str
```

#### SecurityConfigurationDTO (`configurations/security.py`)

Nested configuration for all security settings:

```python
class SecurityConfigurationDTO(BaseModel):
    rate_limiting: RateLimitingConfig
    security_headers: SecurityHeadersConfigDTO
    input_validation: InputValidationConfigDTO
    authentication: AuthenticationConfigDTO
    cors: CORSConfigDTO
```

## File Structure

```
dtos/
├── __init__.py
├── README.md
├── base.py                      # EnhancedBaseModel
├── configurations/
│   ├── __init__.py
│   ├── cache.py                 # Cache configuration DTO
│   ├── db.py                    # Database configuration DTO
│   └── security.py              # Security configuration DTOs
├── requests/
│   ├── __init__.py
│   ├── abstraction.py           # IRequestDTO base class
│   └── user/
│       ├── __init__.py
│       ├── login.py             # Login request DTO
│       ├── logout.py            # Logout request DTO
│       └── registration.py      # Registration request DTO
└── responses/
    ├── __init__.py
    └── base.py                  # BaseResponseDTO
```

## Password Validation Rules

The password validation in request DTOs enforces:

| Requirement | Description |
|-------------|-------------|
| Minimum length | At least 8 characters |
| Uppercase | At least one uppercase letter (A-Z) |
| Lowercase | At least one lowercase letter (a-z) |
| Digit | At least one number (0-9) |
| Special char | At least one of: @$!%*?& |

## Best Practices

1. **Inherit from appropriate base**: Use EnhancedBaseModel for request DTOs
2. **Add field validators**: Custom validation for business rules
3. **Use type hints**: Pydantic uses them for validation
4. **Document fields**: Add docstrings for API documentation
5. **Keep DTOs focused**: One DTO per specific use case
6. **Validate early**: DTOs catch errors at the API boundary

## Adding New DTOs

1. Create the DTO file in the appropriate directory
2. Inherit from IRequestDTO/EnhancedBaseModel for requests
3. Add field validators as needed
4. Add comprehensive docstrings
5. Update this README
