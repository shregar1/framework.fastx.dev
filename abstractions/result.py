"""
Result/Either Pattern.

Provides explicit error handling without exceptions,
making success/failure paths visible in type signatures.

Implements:
- Result type (Success/Failure)
- Monadic operations (map, flatMap, etc.)
- Error aggregation

SOLID Principles:
- Single Responsibility: Encapsulates operation outcome
- Open/Closed: Extensible error types
- Liskov Substitution: Results are interchangeable
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")  # Success type
E = TypeVar("E")  # Error type
U = TypeVar("U")  # Mapped type


class Result(ABC, Generic[T, E]):
    """
    Result type representing either success or failure.

    Usage:
        def divide(a: int, b: int) -> Result[float, str]:
            if b == 0:
                return Failure("Division by zero")
            return Success(a / b)

        result = divide(10, 2)
        if result.is_success:
            print(f"Result: {result.value}")
        else:
            print(f"Error: {result.error}")

        # Or use map/flatMap
        result = divide(10, 2).map(lambda x: x * 2)
    """

    @property
    @abstractmethod
    def is_success(self) -> bool:
        """Check if result is successful."""
        pass

    @property
    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return not self.is_success

    @property
    @abstractmethod
    def value(self) -> T:
        """Get the success value. Raises if failure."""
        pass

    @property
    @abstractmethod
    def error(self) -> E:
        """Get the error. Raises if success."""
        pass

    @abstractmethod
    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        """Map the success value."""
        pass

    @abstractmethod
    def map_error(self, func: Callable[[E], U]) -> "Result[T, U]":
        """Map the error value."""
        pass

    @abstractmethod
    def flat_map(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """Flat map (bind) the success value."""
        pass

    @abstractmethod
    def get_or_else(self, default: T) -> T:
        """Get value or return default."""
        pass

    @abstractmethod
    def get_or_raise(self) -> T:
        """Get value or raise exception."""
        pass

    def on_success(self, func: Callable[[T], None]) -> "Result[T, E]":
        """Execute function if success."""
        if self.is_success:
            func(self.value)
        return self

    def on_failure(self, func: Callable[[E], None]) -> "Result[T, E]":
        """Execute function if failure."""
        if self.is_failure:
            func(self.error)
        return self


@dataclass
class Success(Result[T, E]):
    """Successful result."""

    _value: T

    @property
    def is_success(self) -> bool:
        return True

    @property
    def value(self) -> T:
        return self._value

    @property
    def error(self) -> E:
        raise ValueError("Cannot get error from Success")

    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        return Success(func(self._value))

    def map_error(self, func: Callable[[E], U]) -> Result[T, U]:
        return Success(self._value)

    def flat_map(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return func(self._value)

    def get_or_else(self, default: T) -> T:
        return self._value

    def get_or_raise(self) -> T:
        return self._value


@dataclass
class Failure(Result[T, E]):
    """Failed result."""

    _error: E

    @property
    def is_success(self) -> bool:
        return False

    @property
    def value(self) -> T:
        raise ValueError(f"Cannot get value from Failure: {self._error}")

    @property
    def error(self) -> E:
        return self._error

    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        return Failure(self._error)

    def map_error(self, func: Callable[[E], U]) -> Result[T, U]:
        return Failure(func(self._error))

    def flat_map(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return Failure(self._error)

    def get_or_else(self, default: T) -> T:
        return default

    def get_or_raise(self) -> T:
        if isinstance(self._error, Exception):
            raise self._error
        raise ValueError(str(self._error))


# Convenience functions
def success(value: T) -> Result[T, Any]:
    """Create a successful result."""
    return Success(value)


def failure(error: E) -> Result[Any, E]:
    """Create a failed result."""
    return Failure(error)


def try_catch(func: Callable[[], T]) -> Result[T, Exception]:
    """
    Execute a function and catch exceptions as Result.

    Usage:
        result = try_catch(lambda: risky_operation())
    """
    try:
        return Success(func())
    except Exception as e:
        return Failure(e)


async def try_catch_async(func: Callable[[], T]) -> Result[T, Exception]:
    """Async version of try_catch."""
    try:
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return Success(await func())
        return Success(func())
    except Exception as e:
        return Failure(e)


class ValidationResult(Generic[T]):
    """
    Result type for validation with multiple errors.

    Usage:
        def validate_user(data: dict) -> ValidationResult[User]:
            errors = []
            if not data.get("email"):
                errors.append("Email is required")
            if not data.get("password"):
                errors.append("Password is required")

            if errors:
                return ValidationResult.invalid(errors)
            return ValidationResult.valid(User(**data))
    """

    def __init__(
        self,
        value: Optional[T] = None,
        errors: Optional[List[str]] = None,
    ):
        self._value = value
        self._errors = errors or []

    @property
    def is_valid(self) -> bool:
        return len(self._errors) == 0

    @property
    def value(self) -> T:
        if not self.is_valid:
            raise ValueError(f"Validation failed: {self._errors}")
        return self._value  # type: ignore

    @property
    def errors(self) -> List[str]:
        return self._errors

    @classmethod
    def valid(cls, value: T) -> "ValidationResult[T]":
        return cls(value=value)

    @classmethod
    def invalid(cls, errors: List[str]) -> "ValidationResult[T]":
        return cls(errors=errors)

    def map(self, func: Callable[[T], U]) -> "ValidationResult[U]":
        if self.is_valid:
            return ValidationResult.valid(func(self._value))  # type: ignore
        return ValidationResult.invalid(self._errors)

    def merge(self, other: "ValidationResult[U]") -> "ValidationResult[tuple]":
        """Merge two validation results."""
        all_errors = self._errors + other._errors
        if all_errors:
            return ValidationResult.invalid(all_errors)
        return ValidationResult.valid((self._value, other._value))


@dataclass
class Error:
    """
    Structured error for Result pattern.

    Usage:
        def process() -> Result[Data, Error]:
            if not valid:
                return failure(Error(
                    code="VALIDATION_ERROR",
                    message="Invalid data",
                    details={"field": "email"}
                ))
    """

    code: str
    message: str
    details: Optional[dict] = None

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
