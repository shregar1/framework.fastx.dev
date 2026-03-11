# Repositories

## Overview

The `repositories` module implements the Repository pattern for data access. Repositories abstract database operations, providing a clean interface between business logic and data persistence.

## Purpose

**Repositories** provide:

- **Abstraction**: Hide database implementation details
- **Testability**: Easy to mock for unit tests
- **Reusability**: Common queries in one place
- **Caching**: Built-in LRU cache support
- **Logging**: Query execution time tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Service                                │
│                 (Business logic)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Repository                              │
│   (Data access abstraction with caching and logging)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   SQLAlchemy Session                         │
│              (Database operations)                           │
└─────────────────────────────────────────────────────────────┘
```

## Components

### IRepository (Base Class)

All repositories inherit from `abstractions.repository.IRepository`:

```python
from abstractions.repository import IRepository

class MyRepository(IRepository):
    def __init__(self, session, **kwargs):
        super().__init__(model=MyModel, **kwargs)
        self.session = session
```

**Inherited Methods:**
- `create_record(record)`: Insert new record
- `retrieve_record_by_id(id)`: Find by primary key (cached)
- `retrieve_record_by_urn(urn)`: Find by URN (cached)
- `update_record(id, new_data)`: Update existing record

### UserRepository (`user.py`)

Repository for user data access.

```python
from repositories.user import UserRepository

# Initialize with session
repo = UserRepository(
    urn="urn:req:123",
    user_urn="urn:user:456",
    api_name="LOGIN",
    session=db_session,
    user_id="user-789"
)

# Find user by email
user = repo.retrieve_record_by_email("user@example.com")

# Find user by email and password
user = repo.retrieve_record_by_email_and_password(
    email="user@example.com",
    password=hashed_password
)

# Check login status
user = repo.retrieve_record_by_id_is_logged_in(
    id=123,
    is_logged_in=True
)
```

**Custom Methods:**

| Method | Description |
|--------|-------------|
| `retrieve_record_by_email_and_password` | Login authentication |
| `retrieve_record_by_email` | Find user by email |
| `retrieve_record_by_id_and_is_logged_in` | Check session status (list) |
| `retrieve_record_by_id_is_logged_in` | Check session status (single) |

## Features

### Execution Time Logging

All repository methods log execution time:

```python
def retrieve_record_by_email(self, email):
    start_time = datetime.now()
    record = self.session.query(self.model).filter(...).first()
    execution_time = datetime.now() - start_time
    self.logger.info(f"Execution time: {execution_time} seconds")
    return record
```

### Request Context

Repositories receive request context for logging:

```python
repo = UserRepository(
    urn="urn:req:123",      # Request tracking
    user_urn="urn:user:456", # User identification
    api_name="LOGIN",        # API endpoint
    session=db_session,
    user_id="user-789"
)
```

### Soft Delete Support

All queries filter by `is_deleted` flag:

```python
def retrieve_record_by_email(self, email, is_deleted=False):
    return self.session.query(self.model).filter(
        self.model.email == email,
        self.model.is_deleted == is_deleted  # Soft delete filter
    ).first()
```

## Usage Example

```python
from repositories.user import UserRepository
from models.user import User

# In a service
class UserLoginService(IService):
    def __init__(self, user_repository: UserRepository, **kwargs):
        super().__init__(**kwargs)
        self.user_repository = user_repository
    
    def run(self, request_dto):
        # Use repository for data access
        user = self.user_repository.retrieve_record_by_email_and_password(
            email=request_dto.email,
            password=hashed_password
        )
        
        if not user:
            raise NotFoundError("User not found", ...)
        
        # Update login status
        self.user_repository.update_record(
            id=user.id,
            new_data={
                "is_logged_in": True,
                "last_login": datetime.utcnow()
            }
        )
        
        return user
```

## File Structure

```
repositories/
├── __init__.py
├── README.md
└── user.py          # User repository
```

## Best Practices

1. **Always use repositories**: Never query models directly in services
2. **Pass session explicitly**: Don't use global sessions
3. **Include request context**: URN, user info for logging
4. **Filter soft deletes**: Always include `is_deleted == False`
5. **Log execution time**: Track slow queries
6. **Use caching wisely**: Cache read-heavy, invalidate on writes

## Adding New Repositories

1. Create new file in `repositories/` directory
2. Inherit from `IRepository`
3. Set the model class in `__init__`
4. Add custom query methods
5. Log execution times
6. Filter by `is_deleted`
7. Update this README
