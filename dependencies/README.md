# Dependencies

## Overview

The `dependencies` module provides FastAPI dependency injection components for the FastMVC application. Dependencies are reusable components that can be injected into route handlers, enabling clean separation of concerns and easy testing.

## Purpose

**Dependency Injection (DI)** in FastAPI provides:

- **Decoupling**: Controllers don't create their own dependencies
- **Testability**: Easy to mock dependencies in tests
- **Reusability**: Share common logic across endpoints
- **Request scoping**: Dependencies can access request context

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Controller                               │
│            (uses Depends() to inject)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dependency.derive()                        │
│        (returns factory or shared instance)                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│   Shared Instances      │     │   Factory Functions         │
│   (DB, Cache sessions)  │     │   (Services, Repos, Utils)  │
└─────────────────────────┘     └─────────────────────────────┘
```

## Components

### Core Dependencies

#### DBDependency (`db.py`)

Provides the shared SQLAlchemy database session.

```python
from fastapi import Depends
from dependencies.db import DBDependency
from sqlalchemy.orm import Session

@router.get("/users")
async def get_users(session: Session = Depends(DBDependency.derive)):
    return session.query(User).all()
```

#### CacheDependency (`cache.py`)

Provides the shared Redis cache session.

```python
from fastapi import Depends
from dependencies.cache import CacheDependency
from redis import Redis

@router.get("/cached")
async def get_cached(cache: Redis = Depends(CacheDependency.derive)):
    return cache.get("my_key")
```

### Repository Dependencies

#### UserRepositoryDependency (`repositiories/user.py`)

Factory for creating UserRepository instances with request context.

```python
from dependencies.repositiories.user import UserRepositoryDependency

@router.get("/user/{id}")
async def get_user(
    id: str,
    session: Session = Depends(DBDependency.derive),
    repo_factory: Callable = Depends(UserRepositoryDependency.derive)
):
    repo = repo_factory(
        urn=request.state.urn,
        user_urn=None,
        api_name="GET_USER",
        session=session,
        user_id=id
    )
    return repo.retrieve_record_by_id(id)
```

### Service Dependencies

#### UserLoginServiceDependency (`services/user/login.py`)

Factory for creating UserLoginService instances.

```python
from dependencies.services.user.login import UserLoginServiceDependency

service_factory = Depends(UserLoginServiceDependency.derive)
service = service_factory(
    urn=urn,
    user_urn=user_urn,
    api_name="LOGIN",
    user_id=None,
    jwt_utility=jwt_util,
    user_repository=user_repo
)
result = await service.run(login_dto)
```

#### UserLogoutServiceDependency (`services/user/logout.py`)

Factory for creating UserLogoutService instances.

#### UserRegistrationServiceDependency (`services/user/register.py`)

Factory for creating UserRegistrationService instances.

### Utility Dependencies

#### DictionaryUtilityDependency (`utilities/dictionary.py`)

Factory for creating DictionaryUtility instances.

```python
from dependencies.utilities.dictionary import DictionaryUtilityDependency

util_factory = Depends(DictionaryUtilityDependency.derive)
util = util_factory(urn=urn, user_urn=user_urn, api_name=api_name, user_id=user_id)
camel_data = util.convert_dict_keys_to_camel_case(snake_data)
```

#### JWTUtilityDependency (`utilities/jwt.py`)

Factory for creating JWTUtility instances.

```python
from dependencies.utilities.jwt import JWTUtilityDependency

jwt_factory = Depends(JWTUtilityDependency.derive)
jwt_util = jwt_factory(urn=urn, user_urn=user_urn, api_name=api_name, user_id=user_id)
token = jwt_util.generate_token(payload)
```

## Dependency Patterns

### Pattern 1: Shared Instance

Used for resources that should be shared across requests (DB, Cache).

```python
class DBDependency:
    @staticmethod
    def derive() -> Session:
        return db_session  # Shared instance
```

### Pattern 2: Factory Function

Used when instances need request-specific context.

```python
class UserRepositoryDependency:
    @staticmethod
    def derive() -> Callable:
        def factory(urn, user_urn, api_name, session, user_id):
            return UserRepository(...)
        return factory
```

## Usage in Controllers

```python
class UserLoginController(IUserController):
    async def post(
        self,
        request: Request,
        request_payload: UserLoginRequestDTO,
        # Dependencies are injected by FastAPI
        session: Session = Depends(DBDependency.derive),
        user_repository: UserRepository = Depends(UserRepositoryDependency.derive),
        user_login_service_factory: Callable = Depends(UserLoginServiceDependency.derive),
        dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
        jwt_utility: JWTUtility = Depends(JWTUtilityDependency.derive)
    ) -> JSONResponse:
        # Initialize with request context
        self.user_repository = user_repository(
            urn=self.urn,
            session=session,
            ...
        )
        # Use the repository
        user = self.user_repository.find_by_email(email)
```

## File Structure

```
dependencies/
├── __init__.py
├── README.md
├── cache.py                    # Redis cache dependency
├── db.py                       # Database session dependency
├── repositiories/
│   ├── __init__.py
│   └── user.py                 # User repository factory
├── services/
│   ├── __init__.py
│   └── user/
│       ├── __init__.py
│       ├── login.py            # Login service factory
│       ├── logout.py           # Logout service factory
│       └── register.py         # Registration service factory
└── utilities/
    ├── __init__.py
    ├── dictionary.py           # Dictionary utility factory
    └── jwt.py                  # JWT utility factory
```

## Best Practices

1. **Use factories for request-scoped dependencies**: Pass URN and context
2. **Use shared instances for connection pools**: DB, Cache
3. **Log dependency creation**: Helps with debugging and tracing
4. **Type hint return values**: Improves IDE support and documentation
5. **Keep factories simple**: Just instantiation, no business logic

## Testing

Dependencies make testing easier:

```python
# Mock a dependency
def mock_user_repo_factory():
    def factory(*args, **kwargs):
        return MockUserRepository()
    return factory

# Override in tests
app.dependency_overrides[UserRepositoryDependency.derive] = mock_user_repo_factory
```

