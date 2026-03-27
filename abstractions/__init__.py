"""FastMVC Abstractions Module.

This module provides a comprehensive collection of design pattern
implementations and abstractions for building scalable, maintainable
applications following MVC architecture and SOLID principles.

Patterns Included:
- Repository Pattern: Data access abstraction
- Service Pattern: Business logic encapsulation
- Controller Pattern: Request handling
- Unit of Work: Transaction management
- Specification: Query building
- CQRS: Command/Query separation
- Domain Events: Event-driven architecture
- Result/Either: Error handling without exceptions
- Value Objects: Immutable domain objects
- Mapper: Object transformation
- Validator: Business rule validation
- Pipeline: Chain of responsibility
- Strategy: Interchangeable algorithms
- Observer: Pub/sub notifications
- Decorator: Behavior extension
- Entity/Aggregate: DDD building blocks
- Presenter: View formatting
"""

# I MVC abstractions
from .controller import IController
from .dependency import IDependency
from .dto import AbstractRequestDTO, AbstractResponseDTO
from .error import IError
from .repository import IRepository
from .service import IService
from .utility import IUtility

# Unit of Work Pattern
from .unit_of_work import (
    IUnitOfWork,
    ISyncUnitOfWork,
    IUnitOfWork,
    UnitOfWorkManager,
)

# Specification Pattern
from .specification import (
    ISpecification,
    AndSpecification,
    OrSpecification,
    NotSpecification,
    LambdaSpecification,
    QuerySpecification,
    FilterBuilder,
)

# CQRS Pattern
from .cqrs import (
    ICommand,
    IQuery,
    ICommandHandler,
    IQueryHandler,
    CommandBus,
    QueryBus,
    Mediator,
)

# Domain Events
from .domain_events import (
    IDomainEvent,
    IEventHandler,
    EventDispatcher,
    EventStore,
    AggregateRoot as EventSourcingAggregateRoot,
    event_handler,
)

# Result/Either Pattern
from .result import (
    Result,
    Success,
    Failure,
    success,
    failure,
    try_catch,
    try_catch_async,
    ValidationResult,
    Error,
)

# Value Objects
from .value_object import (
    ValueObject,
    Email,
    Money,
    PhoneNumber,
    Address,
    DateRange,
    Percentage,
    Slug,
)

# Mapper Pattern
from .mapper import (
    IMapper,
    IBidirectionalMapper,
    LambdaMapper,
    CompositeMapper,
    MappingProfile,
    TypeMapping,
    AutoMapper,
)

# Validator Pattern
from .validator import (
    ValidationError,
    ValidationResult as ValidatorResult,
    IValidator,
    IAsyncValidator,
    FluentValidator,
    CompositeValidator,
    ConditionalValidator,
    validate,
)

# Pipeline Pattern
from .pipeline import (
    IPipelineHandler,
    Pipeline,
    SyncPipeline,
    PipelineContext,
    TransformPipeline,
    FilterPipeline,
    pipe,
    async_pipe,
)

# Strategy Pattern
from .strategy import (
    IStrategy,
    IAsyncStrategy,
    StrategyContext,
    StrategyRegistry,
    ConditionalStrategy,
    CompositeStrategy,
    FallbackStrategy,
    LambdaStrategy,
    strategy,
)

# Observer Pattern
from .observer import (
    IObserver,
    IAsyncObserver,
    ISubject,
    Subject,
    AsyncSubject,
    WeakSubject,
    EventChannel,
    EventBus,
    AsyncEventBus,
    LambdaObserver,
    FilteredObserver,
    BufferedObserver,
    on_event,
)

# Decorator Pattern
from .decorator import (
    IComponent,
    IDecorator,
    timing,
    retry,
    cache,
    log_calls,
    validate_args,
    deprecated,
    singleton,
    run_in_thread,
    rate_limit,
    timeout,
)

# Entity/Aggregate Pattern
from .entity import (
    IEntity,
    Entity,
    IAggregateRoot,
    AggregateRoot,
    EntityFactory,
    DomainEvent,
    SoftDeletableEntity,
    AuditableEntity,
    VersionedEntity,
)

# Presenter Pattern
from .presenter import (
    IPresenter,
    ViewModel,
    PaginatedViewModel,
    ApiResponse,
    ResponseBuilder,
    JsonPresenter,
    HtmlPresenter,
    CompositePresenter,
)

__all__ = [
    # I MVC
    "IController",
    "IDependency",
    "AbstractRequestDTO",
    "AbstractResponseDTO",
    "IError",
    "IRepository",
    "IService",
    "IUtility",
    # Unit of Work
    "IUnitOfWork",
    "ISyncUnitOfWork",
    "IUnitOfWork",
    "UnitOfWorkManager",
    # Specification
    "ISpecification",
    "AndSpecification",
    "OrSpecification",
    "NotSpecification",
    "LambdaSpecification",
    "QuerySpecification",
    "FilterBuilder",
    # CQRS
    "ICommand",
    "IQuery",
    "ICommandHandler",
    "IQueryHandler",
    "CommandBus",
    "QueryBus",
    "Mediator",
    # Domain Events
    "IDomainEvent",
    "IEventHandler",
    "EventDispatcher",
    "EventStore",
    "EventSourcingAggregateRoot",
    "event_handler",
    # Result
    "Result",
    "Success",
    "Failure",
    "success",
    "failure",
    "try_catch",
    "try_catch_async",
    "ValidationResult",
    "Error",
    # Value Objects
    "ValueObject",
    "Email",
    "Money",
    "PhoneNumber",
    "Address",
    "DateRange",
    "Percentage",
    "Slug",
    # Mapper
    "IMapper",
    "IBidirectionalMapper",
    "LambdaMapper",
    "CompositeMapper",
    "MappingProfile",
    "TypeMapping",
    "AutoMapper",
    # Validator
    "ValidationError",
    "ValidatorResult",
    "IValidator",
    "IAsyncValidator",
    "FluentValidator",
    "CompositeValidator",
    "ConditionalValidator",
    "validate",
    # Pipeline
    "IPipelineHandler",
    "Pipeline",
    "SyncPipeline",
    "PipelineContext",
    "TransformPipeline",
    "FilterPipeline",
    "pipe",
    "async_pipe",
    # Strategy
    "IStrategy",
    "IAsyncStrategy",
    "StrategyContext",
    "StrategyRegistry",
    "ConditionalStrategy",
    "CompositeStrategy",
    "FallbackStrategy",
    "LambdaStrategy",
    "strategy",
    # Observer
    "IObserver",
    "IAsyncObserver",
    "ISubject",
    "Subject",
    "AsyncSubject",
    "WeakSubject",
    "EventChannel",
    "EventBus",
    "AsyncEventBus",
    "LambdaObserver",
    "FilteredObserver",
    "BufferedObserver",
    "on_event",
    # Decorator
    "IComponent",
    "IDecorator",
    "timing",
    "retry",
    "cache",
    "log_calls",
    "validate_args",
    "deprecated",
    "singleton",
    "run_in_thread",
    "rate_limit",
    "timeout",
    # Entity/Aggregate
    "IEntity",
    "Entity",
    "IAggregateRoot",
    "AggregateRoot",
    "EntityFactory",
    "DomainEvent",
    "SoftDeletableEntity",
    "AuditableEntity",
    "VersionedEntity",
    # Presenter
    "IPresenter",
    "ViewModel",
    "PaginatedViewModel",
    "ApiResponse",
    "ResponseBuilder",
    "JsonPresenter",
    "HtmlPresenter",
    "CompositePresenter",
]
