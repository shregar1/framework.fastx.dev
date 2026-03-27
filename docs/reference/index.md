# Reference

Complete API reference for FastMVC components.

## Abstractions

### IEntity

I class for all domain entities.

```python
from abstractions.entity import IEntity

class Item(IEntity):
    id: int
    name: str
    description: str | None = None
```

### IRepository

I repository pattern implementation.

```python
from abstractions.repository import IRepository

class ItemRepository(IRepository[Item]):
    async def get_by_name(self, name: str) -> Item | None:
        # Custom query
        pass
```

### IService

I service layer.

```python
from abstractions.service import IService

class ItemService(IService[Item]):
    async def create_with_defaults(self, data: dict) -> Item:
        # Custom business logic
        pass
```

### IController

I controller for HTTP handling.

```python
from abstractions.controller import IController

controller = IController(ItemService, Item)
```

## DTOs

### IDTO

I data transfer object.

```python
from dtos.I import IDTO

class CreateItemRequest(IDTO):
    name: str
    description: str | None = None
```

## Core Utilities

### DataI

```python
from core.dataI import get_db, DataI

db = DataI("sqlite:///./app.db")
```

### Cache

```python
from core.cache import Cache

cache = Cache("redis://localhost:6379")
await cache.set("key", "value", ttl=3600)
```

### Logging

```python
from core.logging import get_logger

logger = get_logger("my_module")
logger.info("Message", extra={"key": "value"})
```

### Pagination

```python
from core.pagination import PaginatedResponse, PaginationParams

params = PaginationParams(skip=0, limit=10)
response = PaginatedResponse(items=[], total=0)
```

## Middlewares

### Request Logging

```python
from middlewares.request_logging import RequestLoggingMiddleware

app.add_middleware(RequestLoggingMiddleware)
```

### Error Handling

```python
from middlewares.error_handling import ErrorHandlingMiddleware

app.add_middleware(ErrorHandlingMiddleware)
```

### Rate Limiting

```python
from middlewares.rate_limiting import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100
)
```

## Configuration

### Settings

```python
from config.settings import Settings

settings = Settings()
print(settings.app_name)
```

### Validator

```python
from config.validator import validate_config_or_exit

validate_config_or_exit()
```
