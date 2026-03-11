# Errors

## Overview

The `errors` module provides custom exception classes for the FastMVC application. These exceptions enable structured error handling with consistent response formatting and request context preservation.

## Purpose

Custom error classes provide:

- **Structured responses**: Consistent error format across all endpoints
- **Request context**: URN and user info preserved in error logs
- **HTTP status mapping**: Each error type maps to appropriate status code
- **i18n support**: Machine-readable keys for client-side translation
- **Debugging**: Structured logging with error context

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Controller                               │
│                 (try/except blocks)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Custom Errors                              │
│     (BadInputError, NotFoundError, UnexpectedError)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   IError (Base)                              │
│           (abstractions/error.py)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BaseResponseDTO                            │
│              (Standardized error response)                   │
└─────────────────────────────────────────────────────────────┘
```

## Components

### BadInputError (`bad_input_error.py`)

For invalid user input and validation failures.

```python
from errors.bad_input_error import BadInputError
from http import HTTPStatus

# Email validation failed
raise BadInputError(
    responseMessage="Please provide a valid email address",
    responseKey="error_invalid_email",
    httpStatusCode=HTTPStatus.BAD_REQUEST
)
```

**Common Use Cases:**
- Invalid email format
- Password validation failures
- Missing required fields
- Invalid data types
- Business rule violations

### NotFoundError (`not_found_error.py`)

For missing resources and records.

```python
from errors.not_found_error import NotFoundError
from http import HTTPStatus

# User not found during login
raise NotFoundError(
    responseMessage="No account found with this email",
    responseKey="error_user_not_found",
    httpStatusCode=HTTPStatus.NOT_FOUND
)
```

**Common Use Cases:**
- User account not found
- Database record not found
- Invalid ID references
- Resource doesn't exist

### UnexpectedResponseError (`unexpected_response_error.py`)

For unexpected conditions and external failures.

```python
from errors.unexpected_response_error import UnexpectedResponseError
from http import HTTPStatus

# External service failed
raise UnexpectedResponseError(
    responseMessage="External service returned an invalid response",
    responseKey="error_external_service",
    httpStatusCode=HTTPStatus.BAD_GATEWAY
)
```

**Common Use Cases:**
- External API failures
- Database inconsistencies
- Unexpected null values
- Configuration errors

## Error Response Format

All errors produce consistent JSON responses:

```json
{
    "transactionUrn": "urn:req:abc123",
    "status": "FAILED",
    "responseMessage": "Human-readable error message",
    "responseKey": "error_machine_readable_key",
    "data": {}
}
```

## Controller Error Handling Pattern

```python
class UserLoginController(IUserController):
    async def post(self, request: Request, ...) -> JSONResponse:
        try:
            # Business logic...
            response_dto = await service.run(request_dto)
            httpStatusCode = HTTPStatus.OK
            
        except (BadInputError, UnexpectedResponseError, NotFoundError) as err:
            # Known business errors
            self.logger.error(f"Error: {err}")
            response_dto = BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.FAILED,
                responseMessage=err.responseMessage,
                responseKey=err.responseKey,
                data={},
            )
            httpStatusCode = err.httpStatusCode
            
        except Exception as err:
            # Unknown errors
            self.logger.error(f"Unexpected error: {err}")
            response_dto = BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.FAILED,
                responseMessage="An unexpected error occurred",
                responseKey="error_internal_server_error",
                data={},
            )
            httpStatusCode = HTTPStatus.INTERNAL_SERVER_ERROR

        return JSONResponse(content=..., status_code=httpStatusCode)
```

## Error Attributes

All error classes share these attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `responseMessage` | str | Human-readable error message |
| `responseKey` | str | Machine-readable key for i18n |
| `httpStatusCode` | int | HTTP status code to return |

## HTTP Status Codes

| Error Type | Typical Status Code |
|------------|---------------------|
| BadInputError | 400 Bad Request |
| NotFoundError | 404 Not Found |
| UnexpectedResponseError | 500 Internal Server Error, 502 Bad Gateway |

## Best Practices

1. **Be specific**: Use appropriate error type for the scenario
2. **User-friendly messages**: responseMessage should be understandable
3. **Consistent keys**: Use snake_case for responseKey
4. **Log before raising**: Add context to logs
5. **Don't expose internals**: Hide implementation details from users

## File Structure

```
errors/
├── __init__.py
├── README.md
├── bad_input_error.py       # Validation and input errors
├── not_found_error.py       # Resource not found errors
└── unexpected_response_error.py  # Unexpected condition errors
```

## Adding New Errors

1. Create new file in `errors/` directory
2. Inherit from `IError` base class
3. Accept responseMessage, responseKey, httpStatusCode
4. Document common use cases
5. Update this README

