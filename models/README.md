# Models

## Overview

The `models` module contains SQLAlchemy ORM models that define the database schema. Models map Python classes to database tables, enabling object-oriented database operations.

## Purpose

**ORM Models** provide:

- **Schema definition**: Tables, columns, indexes, constraints
- **Type mapping**: Python types to database types
- **Relationships**: Foreign keys and associations
- **Queries**: Object-oriented database queries
- **Migrations**: Schema evolution tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Repository                               │
│              (Data access layer)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   SQLAlchemy Models                          │
│            (Python classes → Database tables)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL                                │
│              (Physical database)                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Base (`__init__.py`)

The declarative base that all models inherit from.

```python
from models import Base

class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True)
```

### User (`user.py`)

Model for user accounts and authentication.

```python
from models.user import User

# Create a new user
user = User(
    urn="urn:user:abc123",
    email="user@example.com",
    password="$2b$12$...",  # Bcrypt hash
    created_by=1
)

# Query users
active_users = session.query(User).filter(
    User.is_deleted == False
).all()
```

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | BigInteger | Auto-increment primary key |
| `urn` | String | Unique Resource Name |
| `email` | String | Email address (unique) |
| `password` | String | Bcrypt-hashed password |
| `is_deleted` | Boolean | Soft delete flag |
| `last_login` | DateTime | Last login timestamp |
| `is_logged_in` | Boolean | Current login status |
| `created_on` | DateTime | Creation timestamp |
| `created_by` | BigInteger | Creator's user ID |
| `updated_on` | DateTime | Last update timestamp |
| `updated_by` | BigInteger | Updater's user ID |

**Indexes:**
- `ix_user_urn`: Fast URN lookups
- `ix_user_email`: Unique email index
- `ix_user_created_on`: Sorting by creation date

## Database Conventions

### Naming
- Table names: lowercase, singular (e.g., `user`, not `users`)
- Column names: snake_case (e.g., `created_on`)
- Index names: `ix_<table>_<column>` (e.g., `ix_user_email`)

### Audit Fields
All models should include:
- `created_on`: When the record was created
- `created_by`: Who created it
- `updated_on`: When last updated
- `updated_by`: Who updated it

### Soft Deletes
- Use `is_deleted` boolean instead of hard deletes
- Always filter by `is_deleted == False` in queries

### URN (Unique Resource Name)
- Format: `urn:<entity>:<ulid>` (e.g., `urn:user:01ARZ3NDEKTSV4RRFFQ69G5FAV`)
- Used for external API references
- More readable than database IDs

## Usage Examples

### Creating Records

```python
from models.user import User
from datetime import datetime

user = User(
    urn="urn:user:01ARZ3NDEKTSV4RRFFQ69G5FAV",
    email="john@example.com",
    password=bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
    is_deleted=False,
    is_logged_in=False,
    created_on=datetime.utcnow(),
    created_by=1
)
session.add(user)
session.commit()
```

### Querying Records

```python
# Find by email
user = session.query(User).filter(
    User.email == "john@example.com",
    User.is_deleted == False
).first()

# Find logged-in users
logged_in = session.query(User).filter(
    User.is_logged_in == True
).all()
```

### Updating Records

```python
user.is_logged_in = True
user.last_login = datetime.utcnow()
user.updated_on = datetime.utcnow()
user.updated_by = user.id
session.commit()
```

### Soft Deleting Records

```python
user.is_deleted = True
user.updated_on = datetime.utcnow()
user.updated_by = admin_user_id
session.commit()
```

## File Structure

```
models/
├── __init__.py      # Base declarative class
├── README.md        # This documentation
└── user.py          # User account model
```

## Best Practices

1. **Always use Base**: Inherit from the shared Base class
2. **Define __tablename__**: Use constants from `constants.db.table`
3. **Add indexes**: For frequently queried columns
4. **Use soft deletes**: Never hard delete user data
5. **Include audit fields**: Track who/when for changes
6. **Hash passwords**: Never store plaintext passwords
7. **Document columns**: Add docstrings explaining purpose

## Adding New Models

1. Create new file in `models/` directory
2. Import and inherit from Base
3. Define `__tablename__` using constants
4. Add columns with appropriate types
5. Add indexes for query optimization
6. Include standard audit fields
7. Add comprehensive docstrings
8. Update this README
