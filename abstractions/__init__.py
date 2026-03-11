"""
FastMVC Abstractions Module.

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

# Base MVC abstractions
from abstractions.controller import IController
from abstractions.dependency import IDependency
from abstractions.error import IError
from abstractions.repository import IRepository
from abstractions.service import IService
from abstractions.utility import IUtility

# Unit of Work Pattern
from abstractions.unit_of_work import (
    IUnitOfWork,
    ISyncUnitOfWork,
    BaseUnitOfWork,
    UnitOfWorkManager,
)

# Specification Pattern
from abstractions.specification import (
    ISpecification,
    AndSpecification,
    OrSpecification,
    NotSpecification,
    LambdaSpecification,
    QuerySpecification,
    FilterBuilder,
)

# CQRS Pattern
from abstractions.cqrs import (
    ICommand,
    IQuery,
    ICommandHandler,
    IQueryHandler,
    CommandBus,
    QueryBus,
    Mediator,
)

# Domain Events
from abstractions.domain_events import (
    IDomainEvent,
    IEventHandler,
    EventDispatcher,
    EventStore,
    AggregateRoot as EventSourcingAggregateRoot,
    event_handler,
)

# Result/Either Pattern
from abstractions.result import (
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
from abstractions.value_object import (
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
from abstractions.mapper import (
    IMapper,
    IBidirectionalMapper,
    LambdaMapper,
    CompositeMapper,
    MappingProfile,
    TypeMapping,
    AutoMapper,
)

# Validator Pattern
from abstractions.validator import (
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
from abstractions.pipeline import (
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
from abstractions.strategy import (
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
from abstractions.observer import (
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
from abstractions.decorator import (
    IComponent,
    BaseDecorator,
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
from abstractions.entity import (
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
from abstractions.presenter import (
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
    # Base MVC
    "IController",
    "IDependency",
    "IError",
    "IRepository",
    "IService",
    "IUtility",
    # Unit of Work
    "IUnitOfWork",
    "ISyncUnitOfWork",
    "BaseUnitOfWork",
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
    "BaseDecorator",
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
