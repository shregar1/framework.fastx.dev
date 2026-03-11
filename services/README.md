# Services

## Overview

The `services` module contains the business logic layer of the FastMVC application. Services encapsulate domain rules, coordinate between repositories and external systems, and return structured responses.

## Purpose

**Services** provide:

- **Business logic**: Domain rules and workflows
- **Coordination**: Orchestrate repositories and utilities
- **Abstraction**: Hide implementation details from controllers
- **Testability**: Isolated logic for unit testing
- **Reusability**: Shared operations across endpoints

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Controller                              │
│              (HTTP request handling)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Service                                │
│   (Business logic, validation, coordination)                 │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────┐  ┌─────────────────┐
│   Repository    │  │   Utility   │  │  External API   │
│   (Data access) │  │   (Helpers) │  │   (HTTP calls)  │
└─────────────────┘  └─────────────┘  └─────────────────┘
```

## Components

### IService (Base Class)

All services inherit from `abstractions.service.IService`:

```python
from abstractions.service import IService

class MyService(IService):
    def run(self, request_dto: BaseModel) -> dict:
        # Business logic implementation
        return BaseResponseDTO(...)
```

### IUserService (`user/abstraction.py`)

Base class for user-related services.

```python
from services.user.abstraction import IUserService

class MyUserService(IUserService):
    def run(self, request_dto):
        # User-specific business logic
        pass
```

### UserLoginService (`user/login.py`)

Handles user authentication.

```python
from services.user.login import UserLoginService

service = UserLoginService(
    urn="urn:req:123",
    user_repository=user_repo,
    jwt_utility=jwt_util
)
result = await service.run(login_dto)
```

**Flow:**
1. Find user by email
2. Verify password with bcrypt
3. Update login status
4. Generate JWT token
5. Return success with token

**Errors:**
- `NotFoundError`: User not found
- `BadInputError`: Incorrect password

### UserLogoutService (`user/logout.py`)

Handles session termination.

```python
from services.user.logout import UserLogoutService

service = UserLogoutService(
    urn="urn:req:123",
    user_id=user_id,
    user_repository=user_repo
)
result = await service.run()
```

**Flow:**
1. Find logged-in user by ID
2. Update `is_logged_in` to False
3. Return success

### UserRegistrationService (`user/registration.py`)

Handles new user creation.

```python
from services.user.registration import UserRegistrationService

service = UserRegistrationService(
    urn="urn:req:123",
    user_repository=user_repo
)
result = await service.run(registration_dto)
```

**Flow:**
1. Check if email already exists
2. Hash password with bcrypt
3. Create user record
4. Return success with user info

**Errors:**
- `BadInputError`: Email already registered

## Service Response Pattern

All services return `BaseResponseDTO`:

```python
return BaseResponseDTO(
    transactionUrn=self.urn,
    status=APIStatus.SUCCESS,
    responseMessage="Successfully logged in the user.",
    responseKey="success_user_login",
    data={
        "status": True,
        "token": token,
        "user_urn": user.urn,
    },
)
```

## Dependency Injection

Services receive dependencies through constructor:

```python
class UserLoginService(IUserService):
    def __init__(
        self,
        urn: str,
        user_repository: UserRepository,
        jwt_utility: JWTUtility,
        **kwargs
    ):
        super().__init__(urn, **kwargs)
        self._user_repository = user_repository
        self._jwt_utility = jwt_utility
```

## Error Handling

Services raise custom errors that controllers catch:

```python
from errors.not_found_error import NotFoundError
from errors.bad_input_error import BadInputError

# In service
if not user:
    raise NotFoundError(
        responseMessage="User not Found.",
        responseKey="error_user_not_found",
        httpStatusCode=HTTPStatus.NOT_FOUND
    )

if not password_matches:
    raise BadInputError(
        responseMessage="Incorrect password.",
        responseKey="error_incorrect_password",
        httpStatusCode=HTTPStatus.BAD_REQUEST
    )
```

## File Structure

```
services/
├── __init__.py
├── README.md
├── apis/
│   ├── __init__.py
│   ├── abstraction.py
│   └── v1/
│       ├── __init__.py
│       └── abstraction.py
└── user/
    ├── __init__.py
    ├── abstraction.py       # IUserService base class
    ├── login.py             # UserLoginService
    ├── logout.py            # UserLogoutService
    └── registration.py      # UserRegistrationService
```

## Best Practices

1. **Single responsibility**: One service per business operation
2. **Return DTOs**: Always return BaseResponseDTO
3. **Raise custom errors**: Use BadInputError, NotFoundError, etc.
4. **Log operations**: Debug for flow, Info for business events
5. **Never expose internals**: Hide implementation details
6. **Validate in service**: Additional validation beyond DTOs
7. **Hash passwords**: Use bcrypt for password operations

## Adding New Services

1. Create new file in appropriate package
2. Inherit from IService or domain-specific abstraction
3. Implement `run()` method
4. Accept dependencies via constructor
5. Return BaseResponseDTO
6. Create dependency factory in `dependencies/services/`
7. Update this README
