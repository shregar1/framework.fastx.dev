"""
Pipeline/Chain of Responsibility Pattern.

Enables sequential processing through a chain of handlers,
where each handler can process, modify, or short-circuit.

Implements:
- Request pipeline
- Middleware-style processing
- Async pipeline support

SOLID Principles:
- Single Responsibility: Each handler does one thing
- Open/Closed: Add handlers without modification
- Liskov Substitution: Handlers are interchangeable
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, List, Optional, TypeVar, Union

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")
TContext = TypeVar("TContext")


class IPipelineHandler(ABC, Generic[TRequest, TResponse]):
    """
    Pipeline handler interface.

    Each handler processes the request and optionally passes
    to the next handler in the chain.

    Usage:
        class LoggingHandler(IPipelineHandler[Request, Response]):
            async def handle(
                self,
                request: Request,
                next: Callable
            ) -> Response:
                print(f"Processing: {request}")
                response = await next(request)
                print(f"Completed: {response}")
                return response
    """

    @abstractmethod
    async def handle(
        self,
        request: TRequest,
        next: Callable[[TRequest], TResponse],
    ) -> TResponse:
        """
        Handle the request.

        Args:
            request: Incoming request.
            next: Next handler in pipeline.

        Returns:
            Response from processing.
        """
        pass


class Pipeline(Generic[TRequest, TResponse]):
    """
    Request processing pipeline.

    Chains handlers together for sequential processing.

    Usage:
        pipeline = Pipeline()
        pipeline.add(LoggingHandler())
        pipeline.add(AuthenticationHandler())
        pipeline.add(ValidationHandler())
        pipeline.set_handler(MainHandler())

        response = await pipeline.execute(request)
    """

    def __init__(self):
        self._handlers: List[IPipelineHandler[TRequest, TResponse]] = []
        self._final_handler: Optional[Callable[[TRequest], TResponse]] = None

    def add(
        self,
        handler: IPipelineHandler[TRequest, TResponse],
    ) -> "Pipeline[TRequest, TResponse]":
        """Add a handler to the pipeline."""
        self._handlers.append(handler)
        return self

    def set_handler(
        self,
        handler: Callable[[TRequest], TResponse],
    ) -> "Pipeline[TRequest, TResponse]":
        """Set the final handler."""
        self._final_handler = handler
        return self

    async def execute(self, request: TRequest) -> TResponse:
        """
        Execute the pipeline with the given request.

        Args:
            request: Request to process.

        Returns:
            Final response.
        """
        if not self._final_handler:
            raise ValueError("Pipeline requires a final handler")

        # Build chain from end to start
        async def final(req: TRequest) -> TResponse:
            result = self._final_handler(req)
            if hasattr(result, "__await__"):
                return await result
            return result

        current = final

        for handler in reversed(self._handlers):
            prev = current

            async def make_next(h, p):
                async def next_handler(req: TRequest) -> TResponse:
                    return await h.handle(req, p)
                return next_handler

            current = await make_next(handler, prev)

        return await current(request)


class SyncPipeline(Generic[TRequest, TResponse]):
    """Synchronous pipeline."""

    def __init__(self):
        self._handlers: List[Callable] = []
        self._final_handler: Optional[Callable[[TRequest], TResponse]] = None

    def add(
        self,
        handler: Callable[[TRequest, Callable], TResponse],
    ) -> "SyncPipeline[TRequest, TResponse]":
        """Add a handler."""
        self._handlers.append(handler)
        return self

    def set_handler(
        self,
        handler: Callable[[TRequest], TResponse],
    ) -> "SyncPipeline[TRequest, TResponse]":
        """Set final handler."""
        self._final_handler = handler
        return self

    def execute(self, request: TRequest) -> TResponse:
        """Execute the pipeline."""
        if not self._final_handler:
            raise ValueError("Pipeline requires a final handler")

        def build_chain(handlers: List[Callable], final: Callable) -> Callable:
            if not handlers:
                return final

            first, *rest = handlers
            next_handler = build_chain(rest, final)
            return lambda req: first(req, next_handler)

        chain = build_chain(self._handlers, self._final_handler)
        return chain(request)


@dataclass
class PipelineContext(Generic[TRequest]):
    """
    Context passed through pipeline.

    Allows handlers to share data and state.

    Usage:
        context = PipelineContext(request=my_request)
        context.set("user", current_user)
        context.set("trace_id", generate_trace_id())

        # Later in another handler
        user = context.get("user")
    """

    request: TRequest
    _data: dict = None

    def __post_init__(self):
        if self._data is None:
            self._data = {}

    def set(self, key: str, value: Any) -> None:
        """Set context value."""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get context value."""
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._data


class TransformPipeline(Generic[TRequest]):
    """
    Transform pipeline that modifies data through stages.

    Usage:
        pipeline = TransformPipeline()
        pipeline.add(lambda x: x.strip())
        pipeline.add(lambda x: x.lower())
        pipeline.add(lambda x: x.replace(" ", "_"))

        result = pipeline.execute("  Hello World  ")  # "hello_world"
    """

    def __init__(self):
        self._transforms: List[Callable[[TRequest], TRequest]] = []

    def add(
        self,
        transform: Callable[[TRequest], TRequest],
    ) -> "TransformPipeline[TRequest]":
        """Add a transform stage."""
        self._transforms.append(transform)
        return self

    def execute(self, data: TRequest) -> TRequest:
        """Execute all transforms."""
        result = data
        for transform in self._transforms:
            result = transform(result)
        return result


class FilterPipeline(Generic[TRequest]):
    """
    Filter pipeline that removes items not matching criteria.

    Usage:
        pipeline = FilterPipeline()
        pipeline.add(lambda x: x > 0)  # Positive numbers
        pipeline.add(lambda x: x % 2 == 0)  # Even numbers

        result = pipeline.execute([-1, 0, 1, 2, 3, 4, 5, 6])  # [2, 4, 6]
    """

    def __init__(self):
        self._filters: List[Callable[[Any], bool]] = []

    def add(
        self,
        predicate: Callable[[Any], bool],
    ) -> "FilterPipeline[TRequest]":
        """Add a filter."""
        self._filters.append(predicate)
        return self

    def execute(self, items: List[Any]) -> List[Any]:
        """Apply all filters."""
        result = items
        for filter_func in self._filters:
            result = [item for item in result if filter_func(item)]
        return result


def pipe(*functions: Callable) -> Callable:
    """
    Create a pipeline from functions.

    Usage:
        process = pipe(
            lambda x: x.strip(),
            lambda x: x.lower(),
            lambda x: x.split()
        )

        result = process("  Hello World  ")  # ["hello", "world"]
    """
    def pipeline(data: Any) -> Any:
        result = data
        for func in functions:
            result = func(result)
        return result
    return pipeline


async def async_pipe(*functions: Callable) -> Callable:
    """Async version of pipe."""
    async def pipeline(data: Any) -> Any:
        result = data
        for func in functions:
            if hasattr(func, "__call__"):
                result = func(result)
                if hasattr(result, "__await__"):
                    result = await result
        return result
    return pipeline
