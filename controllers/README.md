# Controllers

## Overview

The `controllers` module handles all HTTP request processing in the FastMVC application. Controllers act as the interface between API consumers and the business logic, orchestrating request validation, service calls, and response formatting.

## Purpose

In the MVC (Model-View-Controller) pattern, **controllers** are responsible for:

- **Request handling**: Receiving and parsing HTTP requests
- **Validation**: Ensuring request data meets requirements
- **Orchestration**: Coordinating between services and dependencies
- **Response formatting**: Preparing structured API responses
- **Error handling**: Catching and formatting error responses

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HTTP Request                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Router                            │
│            (controllers/apis/, controllers/user/)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Controller                              │
│   - Validate request                                         │
│   - Initialize dependencies                                  │
│   - Call service                                             │
│   - Format response                                          │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│        Services         │     │      Dependencies           │
│   (Business Logic)      │     │  (DB, Utils, Repos)         │
└─────────────────────────┘     └─────────────────────────────┘
```

## Components

### API Controllers (`apis/`)

Versioned API endpoints for business features.

```
controllers/apis/
├── __init__.py          # Main /api router
├── abstraction.py       # IAPIController base class
└── v1/
    ├── __init__.py      # /api/v1 router
    └── abstraction.py   # IV1APIController base class
```

**Usage:**
```python
from controllers.apis.v1.abstraction import IV1APIController

class ProductController(IV1APIController):
    async def get(self, request: Request) -> JSONResponse:
        # Handle product listing
        pass
```

### User Controllers (`user/`)

Authentication and user management endpoints.

```
controllers/user/
├── __init__.py          # /user router with all routes
├── abstraction.py       # IUserController base class
├── login.py            # POST /user/login
├── logout.py           # POST /user/logout
└── register.py         # POST /user/register
```

**Endpoints:**

| Method | Path | Controller | Description |
|--------|------|------------|-------------|
| POST | `/user/login` | UserLoginController | User authentication |
| POST | `/user/register` | UserRegistrationController | New user registration |
| POST | `/user/logout` | UserLogoutController | Session termination |

## Controller Abstractions

### IController (Base)

All controllers inherit from `abstractions.controller.IController`:

```python
class IController(ABC):
    """Base controller with request context and logging."""
    
    @property
    def urn(self) -> str: ...
    @property
    def user_urn(self) -> str: ...
    @property
    def api_name(self) -> str: ...
    @property
    def user_id(self) -> str: ...
    @property
    def logger(self): ...
    
    async def validate_request(self, ...): ...
```

### Inheritance Hierarchy

```
IController (abstractions/controller.py)
    │
    ├── IUserController (controllers/user/abstraction.py)
    │   ├── UserLoginController
    │   ├── UserLogoutController
    │   └── UserRegistrationController
    │
    └── IAPIController (controllers/apis/abstraction.py)
        └── IV1APIController (controllers/apis/v1/abstraction.py)
            └── (v1 feature controllers)
```

## Request Flow

1. **Request arrives** at FastAPI router
2. **Middleware** adds URN to `request.state`
3. **Dependencies** are injected (DB session, repositories, etc.)
4. **Controller** receives request:
   - Extracts URN and user context
   - Initializes utilities with context
   - Validates request payload
   - Calls appropriate service
   - Formats and returns response
5. **Error handling** catches exceptions and returns structured errors

## Response Format

All controllers return consistent JSON responses:

```json
{
    "transactionUrn": "urn:request:abc123def456",
    "status": "SUCCESS",
    "responseMessage": "Operation completed successfully",
    "responseKey": "success_operation",
    "data": {
        // Response data here
    }
}
```

**Error Response:**
```json
{
    "transactionUrn": "urn:request:abc123def456",
    "status": "FAILED",
    "responseMessage": "Invalid email format",
    "responseKey": "error_invalid_email",
    "data": {}
}
```

## Dependency Injection

Controllers use FastAPI's `Depends()` for dependency injection:

```python
async def post(
    self,
    request: Request,
    request_payload: UserLoginRequestDTO,
    session: Session = Depends(DBDependency.derive),
    user_repository: UserRepository = Depends(UserRepositoryDependency.derive),
    user_login_service_factory: Callable = Depends(UserLoginServiceDependency.derive),
) -> JSONResponse:
    # Dependencies are injected automatically
```

## Error Handling

Controllers handle three types of errors:

1. **Business Errors** (`BadInputError`, `NotFoundError`, `UnexpectedResponseError`):
   - Logged as errors
   - Return appropriate HTTP status from error
   - Include error message in response

2. **Unexpected Exceptions**:
   - Logged as errors
   - Return 500 Internal Server Error
   - Generic error message to client

3. **Validation Errors** (Pydantic):
   - Handled automatically by FastAPI
   - Return 422 Unprocessable Entity

## Best Practices

1. **Keep controllers thin**: Business logic belongs in services
2. **Use dependency injection**: Never instantiate dependencies directly
3. **Log appropriately**: Debug for flow, Error for failures
4. **Return consistent responses**: Always use BaseResponseDTO
5. **Handle all errors**: No unhandled exceptions should escape
6. **Validate early**: Use DTOs for request validation

## File Structure

```
controllers/
├── __init__.py
├── README.md
├── apis/
│   ├── __init__.py          # /api router
│   ├── abstraction.py       # IAPIController
│   └── v1/
│       ├── __init__.py      # /api/v1 router
│       └── abstraction.py   # IV1APIController
└── user/
    ├── __init__.py          # /user router
    ├── abstraction.py       # IUserController
    ├── login.py            # Login controller
    ├── logout.py           # Logout controller
    └── register.py         # Registration controller
```

## Adding New Controllers

1. Create controller file in appropriate directory
2. Inherit from appropriate abstraction (IUserController, IV1APIController, etc.)
3. Implement HTTP method handlers (get, post, put, delete)
4. Register route in `__init__.py` router
5. Add comprehensive docstrings and type hints
