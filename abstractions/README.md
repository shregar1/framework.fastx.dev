# Abstractions

## Overview

The `abstractions` module provides a comprehensive collection of design pattern implementations and base classes that define the architectural contracts for the FastMVC framework. These abstractions enforce consistent patterns across all layers of the application while following **SOLID principles**.

## Purpose

In software engineering, **abstractions** promote:

- **Loose coupling**: Components depend on interfaces, not implementations
- **Testability**: Easy to mock dependencies for unit testing
- **Consistency**: Standardized patterns across the codebase
- **Extensibility**: New implementations can be added without modifying existing code
- **SOLID compliance**: Each pattern adheres to SOLID principles

## Quick Reference

| Pattern | Module | Purpose |
|---------|--------|---------|
| Repository | `repository.py` | Data access abstraction |
| Service | `service.py` | Business logic encapsulation |
| Controller | `controller.py` | HTTP request handling |
| Unit of Work | `unit_of_work.py` | Transaction management |
| Specification | `specification.py` | Complex query building |
| CQRS | `cqrs.py` | Command/Query separation |
| Domain Events | `domain_events.py` | Event-driven architecture |
| Result/Either | `result.py` | Error handling without exceptions |
| Value Objects | `value_object.py` | Immutable domain concepts |
| Mapper | `mapper.py` | Object transformation |
| Validator | `validator.py` | Business rule validation |
| Pipeline | `pipeline.py` | Chain of responsibility |
| Strategy | `strategy.py` | Interchangeable algorithms |
| Observer | `observer.py` | Pub/sub notifications |
| Decorator | `decorator.py` | Behavior extension |
| Entity/Aggregate | `entity.py` | DDD building blocks |
| Presenter | `presenter.py` | View formatting |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Presentation Layer                              │
│   Controllers (IController) ───► Presenters (IPresenter)                │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
┌──────────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐
│   Command Handlers   │  │  Query Handlers │  │      Validators         │
│  (ICommandHandler)   │  │ (IQueryHandler) │  │     (IValidator)        │
└──────────────────────┘  └─────────────────┘  └─────────────────────────┘
                    │                │
                    └────────┬───────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Application Layer                                │
│                    Services (IService) + Pipeline                        │
│              Domain Events + Unit of Work + Strategies                   │
└─────────────────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Repositories  │  │    Utilities    │  │    Factories    │
│  (IRepository)  │  │   (IUtility)    │  │   (IFactory)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Domain Layer                                    │
│        Entities + Aggregates + Value Objects + Specifications            │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Infrastructure Layer                               │
│               Database (SQLAlchemy) + Cache (Redis)                      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core MVC Components

### IController (`controller.py`)

Base class for HTTP request handlers.

```python
from abstractions import IController

class UserController(IController):
    async def validate_request(self, urn, user_urn, request_payload, ...):
        await super().validate_request(...)
        # Custom validation logic
```

### IService (`service.py`)

Base class for business logic services.

```python
from abstractions import IService

class UserRegistrationService(IService):
    def run(self, request_dto: RegistrationDTO) -> dict:
        # Business logic implementation
        return {"status": "success", "user_id": "..."}
```

### IRepository (`repository.py`)

Base class for data access layer with filtering support.

```python
from abstractions import IRepository
from constants.filter_operator import FilterOperator

class UserRepository(IRepository):
    def __init__(self, session, **kwargs):
        super().__init__(model=UserModel, **kwargs)
        self.session = session

    # Use built-in filtering
    users = repo.retrieve_records_by_filter(
        filters=[(UserModel.is_active, FilterOperator.EQUALS, True)]
    )
```

---

## Design Patterns

### Unit of Work (`unit_of_work.py`)

Manages transactions across multiple repositories.

```python
from abstractions import IUnitOfWork, BaseUnitOfWork

class AppUnitOfWork(BaseUnitOfWork):
    @property
    def users(self) -> UserRepository:
        return self.get_repository(UserRepository)
    
    @property
    def orders(self) -> OrderRepository:
        return self.get_repository(OrderRepository)

# Usage
async with unit_of_work as uow:
    user = await uow.users.create(user_data)
    await uow.orders.create(order_data)
    await uow.commit()  # Both succeed or both fail
```

### Specification Pattern (`specification.py`)

Build complex, reusable query specifications.

```python
from abstractions import ISpecification, QuerySpecification

# Object-level specifications
class ActiveUserSpec(ISpecification[User]):
    def is_satisfied_by(self, user: User) -> bool:
        return user.is_active

class PremiumUserSpec(ISpecification[User]):
    def is_satisfied_by(self, user: User) -> bool:
        return user.subscription == "premium"

# Compose with operators
active_premium = ActiveUserSpec() & PremiumUserSpec()
not_premium = ~PremiumUserSpec()

# Query specifications for database
spec = QuerySpecification[User]()
spec.where("is_active").eq(True)
spec.where("age").gte(18)
spec.order_by("created_at", descending=True)
spec.paginate(page=1, page_size=20)
```

### CQRS Pattern (`cqrs.py`)

Separate read and write operations.

```python
from abstractions import ICommand, IQuery, ICommandHandler, IQueryHandler, Mediator
from dataclasses import dataclass

@dataclass
class CreateUserCommand(ICommand):
    email: str
    name: str

@dataclass
class GetUserByIdQuery(IQuery[User]):
    user_id: str

class CreateUserHandler(ICommandHandler[CreateUserCommand]):
    async def handle(self, command: CreateUserCommand) -> str:
        user = User(email=command.email, name=command.name)
        await self.repository.create(user)
        return user.id

class GetUserByIdHandler(IQueryHandler[GetUserByIdQuery, User]):
    async def handle(self, query: GetUserByIdQuery) -> User:
        return await self.repository.get_by_id(query.user_id)

# Usage with Mediator
mediator = Mediator()
mediator.register_command(CreateUserCommand, CreateUserHandler())
mediator.register_query(GetUserByIdQuery, GetUserByIdHandler())

user_id = await mediator.send(CreateUserCommand(email="...", name="..."))
user = await mediator.send(GetUserByIdQuery(user_id=user_id))
```

### Domain Events (`domain_events.py`)

Event-driven architecture for loose coupling.

```python
from abstractions import IDomainEvent, IEventHandler, EventDispatcher
from dataclasses import dataclass

@dataclass
class UserCreatedEvent(IDomainEvent):
    user_id: str
    email: str

class SendWelcomeEmailHandler(IEventHandler[UserCreatedEvent]):
    async def handle(self, event: UserCreatedEvent) -> None:
        await email_service.send_welcome(event.email)

class UpdateAnalyticsHandler(IEventHandler[UserCreatedEvent]):
    async def handle(self, event: UserCreatedEvent) -> None:
        await analytics.track("user_created", event.user_id)

# Setup
dispatcher = EventDispatcher()
dispatcher.subscribe(UserCreatedEvent, SendWelcomeEmailHandler())
dispatcher.subscribe(UserCreatedEvent, UpdateAnalyticsHandler())

# Dispatch
await dispatcher.dispatch(UserCreatedEvent(user_id="123", email="..."))
```

### Result/Either Pattern (`result.py`)

Explicit error handling without exceptions.

```python
from abstractions import Result, Success, Failure, success, failure

def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return failure("Division by zero")
    return success(a / b)

# Usage
result = divide(10, 2)

if result.is_success:
    print(f"Result: {result.value}")  # 5.0
else:
    print(f"Error: {result.error}")

# Functional style with map/flatMap
result = (
    divide(10, 2)
    .map(lambda x: x * 2)           # 10.0
    .flat_map(lambda x: divide(x, 5))  # 2.0
)

# Get with default
value = result.get_or_else(0)
```

### Value Objects (`value_object.py`)

Immutable domain concepts with validation.

```python
from abstractions import Email, Money, Address, DateRange, Percentage
from decimal import Decimal

# Email with validation
email = Email("user@example.com")
print(email.local_part)  # "user"
print(email.domain)      # "example.com"

# Money with currency
price = Money(Decimal("99.99"), "USD")
tax = price * Decimal("0.1")     # Money(9.999, "USD")
total = price + tax               # Money(109.989, "USD")
total_rounded = total.round(2)    # Money(109.99, "USD")

# Percentage calculations
discount = Percentage(15)
discounted_price = price.amount * (1 - discount.as_decimal)

# Date ranges
from datetime import date
holiday = DateRange(start=date(2024, 12, 20), end=date(2025, 1, 5))
print(date.today() in holiday)  # True/False
print(holiday.days)  # Number of days
```

### Mapper Pattern (`mapper.py`)

Transform between object types.

```python
from abstractions import IMapper, MappingProfile, AutoMapper

class UserToUserDTOMapper(IMapper[User, UserDTO]):
    def map(self, source: User) -> UserDTO:
        return UserDTO(
            id=source.id,
            full_name=f"{source.first_name} {source.last_name}",
            email=source.email
        )

# Or use AutoMapper with profiles
profile = MappingProfile()
profile.create_map(User, UserDTO) \
    .for_member("full_name", lambda u: f"{u.first_name} {u.last_name}") \
    .ignore("password")

mapper = AutoMapper()
mapper.add_profile(profile)
user_dto = mapper.map(user, UserDTO)
```

### Validator Pattern (`validator.py`)

Fluent validation for complex rules.

```python
from abstractions import FluentValidator, CompositeValidator

class UserValidator(FluentValidator[User]):
    def __init__(self):
        super().__init__()
        (self
            .rule_for("email", lambda u: u.email)
                .not_empty("Email is required")
                .matches(r"^[^@]+@[^@]+$", "Invalid email format")
            .rule_for("age", lambda u: u.age)
                .greater_than(0, "Age must be positive")
                .less_than(150, "Age must be realistic")
            .must(lambda u: u.email != u.password, "Password cannot be email"))

# Validate
result = UserValidator().validate(user)
if not result.is_valid:
    for error in result.errors:
        print(f"{error.field}: {error.message}")
```

### Pipeline Pattern (`pipeline.py`)

Chain processing steps.

```python
from abstractions import Pipeline, IPipelineHandler, pipe

class LoggingHandler(IPipelineHandler[Request, Response]):
    async def handle(self, request: Request, next) -> Response:
        print(f"Processing: {request}")
        response = await next(request)
        print(f"Completed: {response}")
        return response

class AuthenticationHandler(IPipelineHandler[Request, Response]):
    async def handle(self, request: Request, next) -> Response:
        if not request.is_authenticated:
            raise UnauthorizedError()
        return await next(request)

# Build pipeline
pipeline = Pipeline()
pipeline.add(LoggingHandler())
pipeline.add(AuthenticationHandler())
pipeline.add(ValidationHandler())
pipeline.set_handler(main_handler)

response = await pipeline.execute(request)

# Simple function piping
process = pipe(
    lambda x: x.strip(),
    lambda x: x.lower(),
    lambda x: x.split()
)
result = process("  Hello World  ")  # ["hello", "world"]
```

### Strategy Pattern (`strategy.py`)

Interchangeable algorithms at runtime.

```python
from abstractions import IStrategy, StrategyRegistry, ConditionalStrategy

class PaymentStrategy(IStrategy[Order, PaymentResult]):
    pass

class CreditCardPayment(PaymentStrategy):
    def execute(self, order: Order) -> PaymentResult:
        return process_credit_card(order)

class PayPalPayment(PaymentStrategy):
    def execute(self, order: Order) -> PaymentResult:
        return process_paypal(order)

# Registry-based selection
registry = StrategyRegistry()
registry.register("credit_card", CreditCardPayment())
registry.register("paypal", PayPalPayment())

result = registry.execute("paypal", order)

# Conditional selection
strategy = ConditionalStrategy()
strategy.when(lambda o: o.total > 1000, PremiumPayment())
strategy.when(lambda o: o.is_international, InternationalPayment())
strategy.default(StandardPayment())

result = strategy.execute(order)
```

### Observer Pattern (`observer.py`)

Pub/sub for loose coupling.

```python
from abstractions import EventBus, LambdaObserver, FilteredObserver

bus = EventBus()

# Subscribe to events
bus.subscribe("user.created", LambdaObserver(
    lambda e: send_welcome_email(e.email)
))
bus.subscribe("user.created", LambdaObserver(
    lambda e: create_default_settings(e.user_id)
))

# Filtered observer
bus.subscribe("order.placed", FilteredObserver(
    predicate=lambda e: e.priority == "high",
    handler=lambda e: send_urgent_notification(e)
))

# Publish events
bus.publish("user.created", UserCreatedEvent(user_id="123", email="..."))
```

### Decorator Pattern (`decorator.py`)

Add behavior without modification.

```python
from abstractions import timing, retry, cache, log_calls, rate_limit

@timing
@retry(max_attempts=3, delay=1.0)
@cache(ttl_seconds=60)
async def fetch_user_data(user_id: str):
    return await api.get_user(user_id)

@rate_limit(calls=10, period=60)  # 10 calls per minute
def api_call():
    return make_request()

@log_calls()
def process_order(order_id: str, amount: float):
    return {"status": "processed"}
```

### Entity/Aggregate Pattern (`entity.py`)

DDD building blocks.

```python
from abstractions import Entity, AggregateRoot, SoftDeletableEntity
from dataclasses import dataclass, field
from typing import List

@dataclass
class OrderItem(Entity):
    product_id: str
    quantity: int
    price: float

@dataclass
class Order(AggregateRoot):
    customer_id: str
    items: List[OrderItem] = field(default_factory=list)
    status: str = "pending"
    
    def place(self):
        if not self.items:
            raise ValueError("Cannot place empty order")
        self.status = "placed"
        self._raise_event(OrderPlacedEvent(
            order_id=self.id,
            customer_id=self.customer_id
        ))
    
    def add_item(self, product_id: str, quantity: int, price: float):
        item = OrderItem(product_id=product_id, quantity=quantity, price=price)
        self.items.append(item)
        self.touch()
```

### Presenter Pattern (`presenter.py`)

Format data for presentation.

```python
from abstractions import IPresenter, JsonPresenter, ApiResponse, ResponseBuilder

class UserPresenter(IPresenter[User, UserViewModel]):
    def present(self, user: User) -> UserViewModel:
        return UserViewModel(
            id=user.id,
            display_name=f"{user.first_name} {user.last_name}",
            member_since=user.created_at.strftime("%B %Y")
        )

# JSON presenter with transforms
presenter = JsonPresenter(
    fields=["id", "email", "name"],
    transforms={"created_at": lambda dt: dt.isoformat()}
)

# API response builder
response = (
    ResponseBuilder()
    .with_data(user_dto)
    .with_metadata("request_id", request_id)
    .with_links({"self": f"/users/{user.id}"})
    .build()
)
```

---

## Common Properties

All abstractions share these common properties:

| Property | Type | Description |
|----------|------|-------------|
| `urn` | `str` | Unique Request Number for distributed tracing |
| `user_urn` | `str` | User's unique resource name |
| `api_name` | `str` | Name of the API endpoint |
| `user_id` | `str/int` | Database identifier of the user |
| `logger` | `Logger` | Structured logger bound with context |

## Best Practices

1. **Always call super().__init__()** in subclass constructors
2. **Use request context** for logging and tracing
3. **Implement abstract methods** as defined by the interface
4. **Keep business logic in services**, not controllers
5. **Use repositories for data access**, not direct queries in services
6. **Prefer composition over inheritance** using decorators and strategies
7. **Use Result type** for operations that can fail in expected ways
8. **Emit domain events** for cross-aggregate communication
9. **Use specifications** for reusable query logic
10. **Apply CQRS** when read and write models differ significantly

## File Structure

```
abstractions/
├── __init__.py          # Package exports (all patterns)
├── controller.py        # IController - HTTP request handling
├── cqrs.py              # CQRS - Command/Query separation
├── decorator.py         # Decorator pattern utilities
├── dependency.py        # IDependency - FastAPI DI
├── domain_events.py     # Domain events & event sourcing
├── entity.py            # Entity & Aggregate Root patterns
├── error.py             # IError - Custom exceptions
├── factory.py           # IFactory - Object creation
├── mapper.py            # Object mapping/transformation
├── observer.py          # Observer/Pub-Sub pattern
├── pipeline.py          # Pipeline/Chain of Responsibility
├── presenter.py         # Presenter/ViewModel pattern
├── repository.py        # IRepository - Data access
├── result.py            # Result/Either monad
├── service.py           # IService - Business logic
├── specification.py     # Specification pattern
├── strategy.py          # Strategy pattern
├── unit_of_work.py      # Unit of Work pattern
├── utility.py           # IUtility - Helper functions
├── validator.py         # Fluent validation
├── value_object.py      # Value objects (Email, Money, etc.)
└── README.md            # This documentation
```
