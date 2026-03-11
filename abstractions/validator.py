"""
Validator Pattern.

Encapsulates validation logic for complex business rules
beyond simple field validation.

Implements:
- Fluent validation builder
- Rule chaining
- Composite validators
- Async validation support

SOLID Principles:
- Single Responsibility: Each validator handles one concern
- Open/Closed: Add validators without modification
- Dependency Inversion: Validators depend on abstractions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")


@dataclass
class ValidationError:
    """Represents a single validation error."""

    field: str
    message: str
    code: str = "VALIDATION_ERROR"
    value: Any = None

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"


@dataclass
class ValidationResult:
    """
    Result of validation operation.

    Usage:
        result = validator.validate(data)
        if result.is_valid:
            process(data)
        else:
            for error in result.errors:
                print(error)
    """

    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return len(self.errors) == 0

    def add_error(
        self,
        field: str,
        message: str,
        code: str = "VALIDATION_ERROR",
        value: Any = None,
    ) -> "ValidationResult":
        """Add an error to the result."""
        self.errors.append(ValidationError(field, message, code, value))
        return self

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another validation result."""
        self.errors.extend(other.errors)
        return self

    def get_errors_for_field(self, field: str) -> List[ValidationError]:
        """Get all errors for a specific field."""
        return [e for e in self.errors if e.field == field]

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary format."""
        result: Dict[str, List[str]] = {}
        for error in self.errors:
            if error.field not in result:
                result[error.field] = []
            result[error.field].append(error.message)
        return result


class IValidator(ABC, Generic[T]):
    """
    Abstract validator interface.

    Usage:
        class UserValidator(IValidator[User]):
            def validate(self, obj: User) -> ValidationResult:
                result = ValidationResult()
                if not obj.email:
                    result.add_error("email", "Email is required")
                if len(obj.password) < 8:
                    result.add_error("password", "Must be at least 8 characters")
                return result
    """

    @abstractmethod
    def validate(self, obj: T) -> ValidationResult:
        """
        Validate an object.

        Args:
            obj: Object to validate.

        Returns:
            Validation result with any errors.
        """
        pass


class IAsyncValidator(ABC, Generic[T]):
    """Async validator interface for external validations."""

    @abstractmethod
    async def validate(self, obj: T) -> ValidationResult:
        """Validate asynchronously."""
        pass


class FluentValidator(IValidator[T]):
    """
    Fluent validation builder.

    Usage:
        validator = FluentValidator[User]()
            .rule_for("email", lambda u: u.email)
                .not_empty("Email is required")
                .matches(r"^[^@]+@[^@]+$", "Invalid email format")
            .rule_for("age", lambda u: u.age)
                .greater_than(0, "Age must be positive")
                .less_than(150, "Age must be realistic")
            .must(lambda u: u.email != u.password, "Password cannot be email")

        result = validator.validate(user)
    """

    def __init__(self):
        self._rules: List[Callable[[T], ValidationResult]] = []
        self._current_field: Optional[str] = None
        self._current_getter: Optional[Callable[[T], Any]] = None

    def rule_for(
        self,
        field: str,
        getter: Callable[[T], Any],
    ) -> "FluentValidator[T]":
        """Start defining rules for a field."""
        self._current_field = field
        self._current_getter = getter
        return self

    def not_empty(self, message: str = "Field is required") -> "FluentValidator[T]":
        """Value must not be empty."""
        field = self._current_field
        getter = self._current_getter

        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            value = getter(obj)
            if not value:
                result.add_error(field, message, "REQUIRED", value)
            return result

        self._rules.append(rule)
        return self

    def not_null(self, message: str = "Field cannot be null") -> "FluentValidator[T]":
        """Value must not be null."""
        field = self._current_field
        getter = self._current_getter

        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            if getter(obj) is None:
                result.add_error(field, message, "NULL", None)
            return result

        self._rules.append(rule)
        return self

    def min_length(
        self,
        length: int,
        message: Optional[str] = None,
    ) -> "FluentValidator[T]":
        """Minimum string length."""
        field = self._current_field
        getter = self._current_getter
        msg = message or f"Must be at least {length} characters"

        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            value = getter(obj)
            if value and len(str(value)) < length:
                result.add_error(field, msg, "MIN_LENGTH", value)
            return result

        self._rules.append(rule)
        return self

    def max_length(
        self,
        length: int,
        message: Optional[str] = None,
    ) -> "FluentValidator[T]":
        """Maximum string length."""
        field = self._current_field
        getter = self._current_getter
        msg = message or f"Must be at most {length} characters"

        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            value = getter(obj)
            if value and len(str(value)) > length:
                result.add_error(field, msg, "MAX_LENGTH", value)
            return result

        self._rules.append(rule)
        return self

    def matches(
        self,
        pattern: str,
        message: str = "Invalid format",
    ) -> "FluentValidator[T]":
        """Must match regex pattern."""
        import re
        field = self._current_field
        getter = self._current_getter

        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            value = getter(obj)
            if value and not re.match(pattern, str(value)):
                result.add_error(field, message, "PATTERN", value)
            return result

        self._rules.append(rule)
        return self

    def greater_than(
        self,
        min_value: Union[int, float],
        message: Optional[str] = None,
    ) -> "FluentValidator[T]":
        """Must be greater than value."""
        field = self._current_field
        getter = self._current_getter
        msg = message or f"Must be greater than {min_value}"

        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            value = getter(obj)
            if value is not None and value <= min_value:
                result.add_error(field, msg, "MIN_VALUE", value)
            return result

        self._rules.append(rule)
        return self

    def less_than(
        self,
        max_value: Union[int, float],
        message: Optional[str] = None,
    ) -> "FluentValidator[T]":
        """Must be less than value."""
        field = self._current_field
        getter = self._current_getter
        msg = message or f"Must be less than {max_value}"

        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            value = getter(obj)
            if value is not None and value >= max_value:
                result.add_error(field, msg, "MAX_VALUE", value)
            return result

        self._rules.append(rule)
        return self

    def in_list(
        self,
        allowed: List[Any],
        message: Optional[str] = None,
    ) -> "FluentValidator[T]":
        """Must be in list of allowed values."""
        field = self._current_field
        getter = self._current_getter
        msg = message or f"Must be one of: {', '.join(str(v) for v in allowed)}"

        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            value = getter(obj)
            if value is not None and value not in allowed:
                result.add_error(field, msg, "NOT_IN_LIST", value)
            return result

        self._rules.append(rule)
        return self

    def must(
        self,
        predicate: Callable[[T], bool],
        message: str,
        field: str = "_",
    ) -> "FluentValidator[T]":
        """Custom validation rule."""
        def rule(obj: T) -> ValidationResult:
            result = ValidationResult()
            if not predicate(obj):
                result.add_error(field, message, "CUSTOM")
            return result

        self._rules.append(rule)
        return self

    def validate(self, obj: T) -> ValidationResult:
        """Run all validation rules."""
        result = ValidationResult()
        for rule in self._rules:
            result.merge(rule(obj))
        return result


class CompositeValidator(IValidator[T]):
    """
    Combines multiple validators.

    Usage:
        composite = CompositeValidator([
            EmailValidator(),
            PasswordValidator(),
            AgeValidator()
        ])
        result = composite.validate(user)
    """

    def __init__(self, validators: List[IValidator[T]]):
        self._validators = validators

    def validate(self, obj: T) -> ValidationResult:
        result = ValidationResult()
        for validator in self._validators:
            result.merge(validator.validate(obj))
        return result


class ConditionalValidator(IValidator[T]):
    """
    Validates only when condition is met.

    Usage:
        validator = ConditionalValidator(
            condition=lambda u: u.is_premium,
            validator=PremiumUserValidator()
        )
    """

    def __init__(
        self,
        condition: Callable[[T], bool],
        validator: IValidator[T],
    ):
        self._condition = condition
        self._validator = validator

    def validate(self, obj: T) -> ValidationResult:
        if self._condition(obj):
            return self._validator.validate(obj)
        return ValidationResult()


def validate(obj: T, validator: IValidator[T]) -> T:
    """
    Validate object and raise if invalid.

    Usage:
        validated_user = validate(user, UserValidator())
    """
    result = validator.validate(obj)
    if not result.is_valid:
        error_msg = "; ".join(str(e) for e in result.errors)
        raise ValueError(f"Validation failed: {error_msg}")
    return obj
